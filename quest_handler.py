"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Completed Code

Name: Khalil Smith

AI Usage: I defined the module structure, all required function signatures, 
          and the quest flow logic. The AI assisted with implementing the 
          detailed requirement checking in accept_quest, the prerequisite 
          chain tracing logic (using a loop to follow backwards links), 
          and the stat calculation/display functions, ensuring proper 
          exception handling throughout.
"""

from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)

# ============================================================================
# REQUIRED FUNCTIONS FROM CHARACTER MANAGER (Implemented Simply for Standalone)
# ============================================================================
# NOTE: These functions must be replaced by the actual implementations 
# from character_manager.py when run in the full game environment. 
# They are named correctly as requested.

def gain_experience(character, xp_amount):
    """Placeholder for character_manager.gain_experience"""
    character['experience'] = character.get('experience', 0) + xp_amount
    # Basic stat update logic omitted, assumes full logic in character_manager
    return False

def add_gold(character, amount):
    """Placeholder for character_manager.add_gold"""
    character['gold'] = character.get('gold', 0) + amount
    if character['gold'] < 0:
        character['gold'] = 0 # Prevent negative gold in simple placeholder
    return character['gold']

# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    """
    Accept a new quest
    
    Raises: QuestNotFoundError, InsufficientLevelError, 
            QuestRequirementsNotMetError, QuestAlreadyCompletedError
    """
    
    # Check quest exists
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest ID '{quest_id}' not found.")
        
    quest = quest_data_dict[quest_id]
    
    # Check not already completed
    if is_quest_completed(character, quest_id):
        raise QuestAlreadyCompletedError(f"Quest '{quest_id}' has already been completed.")
        
    # Check not already active
    if is_quest_active(character, quest_id):
        return True # Already accepted, treat as successful acceptance
        
    # Check level requirement
    required_level = int(quest.get('required_level', 1))
    if character.get('level', 1) < required_level:
        raise InsufficientLevelError(f"Character level {character.get('level')} is too low. Required level: {required_level}.")
        
    # Check prerequisite (if not "NONE")
    prereq_id = quest.get('prerequisite', 'NONE')
    if prereq_id and prereq_id != "NONE":
        if not is_quest_completed(character, prereq_id):
            raise QuestRequirementsNotMetError(f"Prerequisite quest '{prereq_id}' must be completed first.")
            
    # Add to character['active_quests']
    if 'active_quests' not in character:
        character['active_quests'] = []
    character['active_quests'].append(quest_id)
    
    return True


def complete_quest(character, quest_id, quest_data_dict):
    """
    Complete an active quest and grant rewards
    """
    
    # Check quest exists
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest ID '{quest_id}' not found.")
        
    quest = quest_data_dict[quest_id]
    
    # Check quest is active
    if not is_quest_active(character, quest_id):
        raise QuestNotActiveError(f"Quest '{quest_id}' is not currently active.")
        
    # Remove from active_quests
    new_active_quests = []
    removed = False
    i = 0
    while i < len(character['active_quests']):
        current_quest = character['active_quests'][i]
        if current_quest == quest_id and not removed:
            removed = True
        else:
            new_active_quests.append(current_quest)
        i += 1
    character['active_quests'] = new_active_quests
        
    # Add to completed_quests
    if 'completed_quests' not in character:
        character['completed_quests'] = []
    character['completed_quests'].append(quest_id)
    
    # Grant rewards (using the correctly named functions)
    reward_xp = int(quest.get('reward_xp', 0))
    reward_gold = int(quest.get('reward_gold', 0))
    
    gain_experience(character, reward_xp)
    add_gold(character, reward_gold)
    
    # Return reward summary
    return {
        "quest_id": quest_id,
        "reward_xp": reward_xp,
        "reward_gold": reward_gold
    }

def abandon_quest(character, quest_id):
    """
    Remove a quest from active quests without completing it
    
    Raises: QuestNotActiveError if quest not active
    """
    if not is_quest_active(character, quest_id):
        raise QuestNotActiveError(f"Quest '{quest_id}' is not currently active and cannot be abandoned.")
        
    # Remove from active_quests
    new_active_quests = []
    removed = False
    i = 0
    while i < len(character['active_quests']):
        current_quest = character['active_quests'][i]
        if current_quest == quest_id and not removed:
            removed = True
        else:
            new_active_quests.append(current_quest)
        i += 1
    character['active_quests'] = new_active_quests
    
    return True

def get_active_quests(character, quest_data_dict):
    """
    Get full data for all active quests
    """
    active_list = character.get('active_quests', [])
    quest_list = []
    
    # Look up each quest_id in character['active_quests']
    i = 0
    while i < len(active_list):
        quest_id = active_list[i]
        if quest_id in quest_data_dict:
            quest_list.append(quest_data_dict[quest_id])
        i += 1
        
    return quest_list

def get_completed_quests(character, quest_data_dict):
    """
    Get full data for all completed quests
    """
    completed_list = character.get('completed_quests', [])
    quest_list = []
    
    # Look up each quest_id in character['completed_quests']
    i = 0
    while i < len(completed_list):
        quest_id = completed_list[i]
        if quest_id in quest_data_dict:
            quest_list.append(quest_data_dict[quest_id])
        i += 1
        
    return quest_list

def get_available_quests(character, quest_data_dict):
    """
    Get quests that character can currently accept
    
    Available = meets level req + prerequisite done + not completed + not active
    """
    available_list = []
    all_quest_ids = list(quest_data_dict.keys())
    
    i = 0
    while i < len(all_quest_ids):
        quest_id = all_quest_ids[i]
        
        # Filter all quests by requirements
        if can_accept_quest(character, quest_id, quest_data_dict):
            available_list.append(quest_data_dict[quest_id])
        i += 1
        
    return available_list

# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    """
    Check if a specific quest has been completed
    """
    return quest_id in character.get('completed_quests', [])

def is_quest_active(character, quest_id):
    """
    Check if a specific quest is currently active
    """
    return quest_id in character.get('active_quests', [])

def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Check if character meets all requirements to accept quest
    
    Returns: True if can accept, False otherwise
    """
    
    if quest_id not in quest_data_dict:
        return False

    quest = quest_data_dict[quest_id]
    
    # 1. Quest not already completed
    if is_quest_completed(character, quest_id):
        return False
        
    # 2. Quest not already active
    if is_quest_active(character, quest_id):
        return False
        
    # 3. Character level >= quest required_level
    required_level = int(quest.get('required_level', 1))
    if character.get('level', 1) < required_level:
        return False
        
    # 4. Prerequisite quest completed (if any)
    prereq_id = quest.get('prerequisite', 'NONE')
    if prereq_id and prereq_id != "NONE":
        if not is_quest_completed(character, prereq_id):
            return False
            
    return True

def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """
    Get the full chain of prerequisites for a quest
    
    Raises: QuestNotFoundError if quest doesn't exist
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest ID '{quest_id}' not found.")

    chain = []
    current_id = quest_id
    
    # Follow prerequisite links backwards
    while current_id and current_id != "NONE":
        chain.append(current_id)
        
        # Check if the current ID is actually in the dictionary
        if current_id not in quest_data_dict:
            # Found a break in the chain (a prereq that doesn't exist)
            chain.append("INVALID_PREREQUISITE")
            break

        current_id = quest_data_dict[current_id].get('prerequisite', 'NONE')

    # Build list in reverse order [earliest_prereq, ..., quest_id]
    reversed_chain = []
    i = len(chain) - 1
    while i >= 0:
        reversed_chain.append(chain[i])
        i -= 1
        
    return reversed_chain

# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    """
    Calculate what percentage of all quests have been completed
    """
    total_quests = len(quest_data_dict)
    
    if total_quests == 0:
        return 0.0
        
    completed_quests = len(character.get('completed_quests', []))
    
    # percentage = (completed / total) * 100
    percentage = (float(completed_quests) / total_quests) * 100
    
    return percentage

def get_total_quest_rewards_earned(character, quest_data_dict):
    """
    Calculate total XP and gold earned from completed quests
    """
    total_xp = 0
    total_gold = 0
    completed_list = character.get('completed_quests', [])
    
    # Sum up reward_xp and reward_gold for all completed quests
    i = 0
    while i < len(completed_list):
        quest_id = completed_list[i]
        quest = quest_data_dict.get(quest_id)
        
        if quest:
            total_xp += int(quest.get('reward_xp', 0))
            total_gold += int(quest.get('reward_gold', 0))
        i += 1
        
    # Returns: Dictionary with 'total_xp' and 'total_gold'
    return {
        'total_xp': total_xp,
        'total_gold': total_gold
    }

def get_quests_by_level(quest_data_dict, min_level, max_level):
    """
    Get all quests within a level range
    """
    min_level = int(min_level)
    max_level = int(max_level)
    
    filtered_quests = []
    all_quest_ids = list(quest_data_dict.keys())
    
    # Filter all quests by required_level
    i = 0
    while i < len(all_quest_ids):
        quest_id = all_quest_ids[i]
        quest = quest_data_dict[quest_id]
        required_level = int(quest.get('required_level', 1))
        
        if required_level >= min_level and required_level <= max_level:
            filtered_quests.append(quest)
        i += 1
        
    return filtered_quests

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_quest_info(quest_data):
    """
    Display formatted quest information
    """
    print(f"\n=== {quest_data.get('title', 'N/A')} ===")
    print(f"ID: {quest_data.get('quest_id', 'N/A')}")
    print(f"Description: {quest_data.get('description', 'No description.')}")
    
    # Rewards
    xp = quest_data.get('reward_xp', 0)
    gold = quest_data.get('reward_gold', 0)
    print(f"Rewards: {xp} XP, {gold} Gold")
    
    # Requirements
    req_level = quest_data.get('required_level', 1)
    prereq = quest_data.get('prerequisite', 'NONE')
    print(f"Requirements: Level {req_level}")
    if prereq and prereq != "NONE":
        print(f"Prerequisite: {prereq}")
    else:
        print("Prerequisite: None")
        
def display_quest_list(quest_list):
    """
    Display a list of quests in summary format
    """
    if not quest_list:
        print("No quests to display.")
        return
        
    print("\n| {:<20} | {:<5} | {:<5} | {:<5} |".format("Title", "Level", "XP", "Gold"))
    print("-" * 43)

    i = 0
    while i < len(quest_list):
        quest = quest_list[i]
        title = quest.get('title', 'N/A')
        req_level = quest.get('required_level', 1)
        reward_xp = quest.get('reward_xp', 0)
        reward_gold = quest.get('reward_gold', 0)
        
        print("| {:<20} | {:<5} | {:<5} | {:<5} |".format(
            title, req_level, reward_xp, reward_gold
        ))
        i += 1


def display_character_quest_progress(character, quest_data_dict):
    """
    Display character's quest statistics and progress
    """
    
    total_rewards = get_total_quest_rewards_earned(character, quest_data_dict)
    percentage = get_quest_completion_percentage(character, quest_data_dict)
    
    print("\n=== QUEST PROGRESS ===")
    print(f"Active Quests: {len(character.get('active_quests', []))}")
    print(f"Completed Quests: {len(character.get('completed_quests', []))}")
    print(f"Completion Percentage: {percentage:.2f}%")
    print(f"Total XP Earned: {total_rewards['total_xp']}")
    print(f"Total Gold Earned: {total_rewards['total_gold']}")


# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    """
    Validate that all quest prerequisites exist
    
    Checks that every prerequisite (that's not "NONE") refers to a real quest
    
    Raises: QuestNotFoundError if invalid prerequisite found
    """
    all_quest_ids = list(quest_data_dict.keys())
    
    # Check each quest's prerequisite
    i = 0
    while i < len(all_quest_ids):
        quest_id = all_quest_ids[i]
        quest = quest_data_dict[quest_id]
        prereq = quest.get('prerequisite', 'NONE')
        
        # Ensure prerequisite exists in quest_data_dict
        if prereq and prereq != "NONE":
            if prereq not in quest_data_dict:
                raise QuestNotFoundError(f"Quest '{quest_id}' requires missing prerequisite quest ID: '{prereq}'.")
        i += 1
        
    return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== QUEST HANDLER TEST ===")
    
    # Test data
    # test_char = {
    #     'level': 1,
    #     'active_quests': [],
    #     'completed_quests': [],
    #     'experience': 0,
    #     'gold': 100
    # }
    #
    # test_quests = {
    #     'first_quest': {
    #         'quest_id': 'first_quest',
    #         'title': 'First Steps',
    #         'description': 'Complete your first quest',
    #         'reward_xp': 50,
    #         'reward_gold': 25,
    #         'required_level': 1,
    #         'prerequisite': 'NONE'
    #     }
    # }
    #
    # try:
    #     accept_quest(test_char, 'first_quest', test_quests)
    #     print("Quest accepted!")
    # except QuestRequirementsNotMetError as e:
    #     print(f"Cannot accept: {e}")
    #     accept_quest(test_char, 'first_quest', test_quests)
    #     print("Quest accepted!")
    # except QuestRequirementsNotMetError as e:
    #     print(f"Cannot accept: {e}")

