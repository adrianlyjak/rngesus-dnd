rnges.us A python web application for generating role playing games, where an AI is the dungeon master and game author.

Landing Page:
- Introduces the concept
- a big button encouraging visitors to play, going to the Game screen

Game screen:
- List of past campaigns which may be clicked on to resume a campaign, going to the play screen.
- Button to start a new campaign.

New campaign: 
- Text input to describe the type of RPG game, such as details about game context classic, futuristic, funny, etc.
- Button to submit and continue to character list. Text input must not be blank to continue

Character list:
- Lists all current characters as tiles that show their character name. Characters may be removed by clicking an x in the corner
- Button to add a new character that goes to the character creation screen
- A button to continue to the play screen with the current characters

Character Creation:
- A button to "role" a new character. Whenever a new character is roled, the AI generates:
- a random character role. The character role describes their skills and profession.
- a random character type. This is their socio-ethnic background.
- An (editable) character backstory
- A set of 6 attribute scores
- An (editable) primary goal 
- A list of inventory items
- A button to continue with the selected character and return to the character list. Character is persisted and added to the group, now displaying alongside any previously added characters


The play screen:
- A chat interface where the players communicate with the AI Dungeon Master
- All chat history is recorded
- The dungeon master sets the scene first, and asks the players for their actions
- Players describe their actions through the chat interface
- The AI dungeon master has access to a random number generator for dice roles.
- The AI dungeon master leads the players through a story of intrige and adventure



Technology: 

Player interactions should go through a server, and player data should be stored in an sqlite database so that they can resume their play

UI Should be very barebones server side rendered templates

Libraries:

Choose whatever you think is a simple, robust, easy to use python library for the use case.

You can interact with the the AI by import from `rngesus` functions for interfacing with the AI. The AI may be talked to in order
to tell it what to do, or what role to be in. For example

```python
import rngesus

rngesus.prompt("Generate a concept for a RPG game set in space")
# Response "The game takes place in a multi-star cluster, named the Nebular Frontier, in a distant galaxy ..."
```
