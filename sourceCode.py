import copy

def readFile(filename): # read the input file
  f = open(filename, "r")

  initialState = []
  for x in range(4):  # get the initial state
      currLine = f.readline()
      lineArray = currLine.split()
      lineArray = [int(x) for x in lineArray]
      initialState.append(lineArray)

  f.readline()  # read blank line

  goalState = []
  for x in range(4):  # get the goal state
      currLine = f.readline()
      lineArray = currLine.split()
      lineArray = [int(x) for x in lineArray]
      goalState.append(lineArray)
  
  goalStateDict = {}  # turn goal state into dictionary for easy h(x) calculations down the line
  for i in range(4):
      for j in range(4):
          goalStateDict[goalState[i][j]] = (i, j)
  
  f.close()
  return initialState, goalStateDict  # return initial and goal states

def writeOutput(oldFilename, newFilename, path, d, N, fs):  # write the output txt file
  f = open(oldFilename, "r")
  o = open(newFilename, "w")
  
  for x in range(9):  # copy the first 9 lines from the input file
      o.write(f.readline())
  f.close()
  
  o.write('\n') # line break
  o.write(str(d) + '\n')  # depth level
  o.write(str(N) + '\n')  # number of nodes generated
  o.write(' '.join(path) + '\n')  # path from initial state to gaol
  o.write(' '.join(fs)) # each states f(x) value
  
  o.close()

class Node: # node class to keep track
    def __init__(self, state, parent):
      self.parent = parent
      self.state = state
      self.g = 0
      self.h = 0
      self.f = 0
      self.action = []

def getH(currState, goalState): # calculate manhattan distance h(x) given a state
  totalCost = 0
  
  currStateDict = {}
  for i in range(4):
    for j in range(4):
      currStateDict[currState.state[i][j]] = (i, j)
  
  for num in range(1, 16):
    currCost = abs(currStateDict[num][0]-goalState[num][0]) + abs(currStateDict[num][1]-goalState[num][1])
    totalCost += currCost
      
  currState.h = totalCost
  return totalCost

def getG(currState):  # calculate step cost g(x) of a given state
  gCost = 0
  parent = currState.parent
  while parent is not None:
    gCost += 1
    parent = parent.parent

  currState.g = gCost
  return gCost

def getF(currState, goalState): # get total f(x) of a state
  getG(currState)
  getH(currState, goalState)
  currState.f = currState.g + currState.h # f(x) = g(x) + h(x)

def getSmallestCost(generatedNodes):  # get the node with the smallest f(x)
  smallestCost = generatedNodes[0].f
  result = generatedNodes[0]
  result_i = 0
  for i in range(len(generatedNodes)):  # compare all the nodes passed and return the one with the smallest cost
    if (generatedNodes[i].f < smallestCost):
      result = generatedNodes[i]
      result_i = i
  return result, result_i

def getNewState(currState, action): # creates a new node given the current position and an action
  newState = None
  
  for i in range(4):  # find the empty position on the slide puzzle (where the zero is)
    for j in range (4):
      if (currState.state[i][j] == 0):
        zerothX, zerothY  = i, j
  
  position = copy.deepcopy(currState.state)
  if (action == 'L' and zerothY!=0):  # check if action is valid and then find new position based off the given action
    position[zerothX][zerothY], position[zerothX][zerothY-1] = position[zerothX][zerothY-1], position[zerothX][zerothY]
  elif (action == 'R' and zerothY!=3):
    position[zerothX][zerothY], position[zerothX][zerothY+1] = position[zerothX][zerothY+1], position[zerothX][zerothY]
  elif (action == 'U' and zerothX!=0):
    position[zerothX][zerothY], position[zerothX-1][zerothY] = position[zerothX-1][zerothY], position[zerothX][zerothY]
  elif (action == 'D' and zerothX!=3):
    position[zerothX][zerothY], position[zerothX+1][zerothY] = position[zerothX+1][zerothY], position[zerothX][zerothY]
  res = Node(position, currState)
  res.action = action
  return res

def isGenerated(generatedNodes, currNode):  # check if the board position is already in a group of nodes
  result = False
  for node in generatedNodes:
    if (node.state == currNode.state):
      result = True
  return result

def search(initialState, goalState):  # A* search
  initialState = Node(initialState, None) # make initial state node and get its f(x)
  getF(initialState, goalState)
  
  generatedNodes = [initialState] # all newly generated nodes go here
  visitedNodes = []               # all visited nodes go here
  
  while (generatedNodes != []): # while there are nodes not visited
    smallestNode, index = getSmallestCost(generatedNodes) # get the smallest non-visited node
    generatedNodes.pop(index) # take it out of generated ind into visited
    visitedNodes.append(smallestNode)

    if (smallestNode.h == 0): # if the visited node has an h(x)=0 and is the smallest current node, it is the goal node
      finalPath = []  # get path
      parent = smallestNode.parent
      currentNode = smallestNode
      while (parent is not None):
        finalPath.append((currentNode.action, currentNode.f)) # add action from each parent node
        currentNode, parent = parent, parent.parent
      finalPath.append(('', currentNode.f))
      finalPath.reverse() # get path order from start to goal
      return finalPath, smallestNode.g, (len(visitedNodes)+len(generatedNodes)) # return final path, f(x) values, d, and N
              
    nextActions = ['L', 'R', 'U', 'D']  # if it's not the goal, expand the node
    for action in nextActions:
      newState = getNewState(smallestNode, action)  # for each action try to see if you can generate a valid node
      if (not isGenerated(visitedNodes, newState)) and (not isGenerated(generatedNodes, newState)): # if not generated or visited
        getF(newState, goalState)
        generatedNodes.append(newState) # add it to generated nodes
  return None # if no path is found return None

def main(inputFilename, outputFilename):            # main function that, when called, executes all the functions to
                                                    #find the optimal path and write the output file
  initialState, goalState = readFile(inputFilename)   
  result = search(initialState, goalState)  # get result from A* search
  if result is None:  # if no path is found
    print('No path found')
    return

  l, d, N = result  # prep everything for output file
  path = [l[p][0] for p in range(1, len(l))]
  f = [str(x[1]) for x in l]
  # print(path, d, N, f)
  writeOutput(inputFilename, outputFilename, path, d, N, f) # write the output file

main('Input1.txt', 'Output1.txt')