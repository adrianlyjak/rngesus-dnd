the app is: rngesus

the files we have decided to generate are: main.py, templates/landing.html, templates/game.html, templates/new_campaign.html, templates/character_list.html, templates/character_creation.html, templates/play.html, rngesus.py, database.py, static/styles.css

Shared dependencies:

1. Exported variables:
   - None

2. Data schemas:
   - Campaign (id, description, status)
   - Character (id, campaign_id, role, type, backstory, attributes, primary_goal, inventory)
   - Chat (id, campaign_id, user_type, message)

3. DOM element id names:
   - play_button (Landing Page)
   - past_campaigns (Game screen)
   - new_campaign_button (Game screen)
   - campaign_description (New campaign)
   - submit_campaign (New campaign)
   - character_tiles (Character list)
   - remove_character (Character list)
   - add_character_button (Character list)
   - continue_characters (Character list)
   - roll_character_button (Character Creation)
   - character_class (Character Creation)
   - character_type (Character Creation)
   - character_backstory (Character Creation)
   - character_attributes (Character Creation)
   - character_primary_goal (Character Creation)
   - character_inventory (Character Creation)
   - continue_character_creation (Character Creation)
   - chat_interface (Play screen)
   - chat_history (Play screen)
   - chat_input (Play screen)

4. Message names:
   - None

5. Function names:
   - rngesus.prompt (AI interaction)
   - create_campaign (database.py)
   - get_campaigns (database.py)
   - update_campaign (database.py)
   - delete_campaign (database.py)
   - create_character (database.py)
   - get_characters (database.py)
   - update_character (database.py)
   - delete_character (database.py)
   - add_chat_message (database.py)
   - get_chat_history (database.py)