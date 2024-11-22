"""
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   Tool Description:
       Performs chain combos in Another Force during KOF Symphony battles
       with chosen fighter in menu.

   Usage:
   -------------
   Supply the Android device to the command line with -s {android_sn}.
   The tool will automatically provide a continuous prompt to send command
   outputs.
"""
import android_adb as Android
import argparse
import time
import yaml

YAML_FILE="kof_symphony_commmand_list.yaml"
COMMAND_BUTTONS = {
    "LP": (0.35, 0.75),
    "HP": (0.50, 0.75),
    "LK": (0.65, 0.75),
    "HK": (0.85, 0.75),
    "AF": (0.87, 0.15)
}


def obtain_device_configuration(args):
    """ 
        Connect to the Android phone and return the handle to interact with
        as well as the screen size.
    """
    # Connect to the Android Phone.
    return Android.AndroidUSB(device_sn=args.serial_number, verbose=args.verbose)


def obtain_kof_battle_buttons(screen_size):
    """ Returns dictionary of x and y coordinates for tapping the appropriate buttons. """
    another_force = (int(screen_size[0] * COMMAND_BUTTONS["AF"][0]), int(screen_size[1] * COMMAND_BUTTONS["AF"][1]))
    light_punch = (int(screen_size[0] * COMMAND_BUTTONS["LP"][0]), int(screen_size[1] * COMMAND_BUTTONS["LP"][1]))
    heavy_punch = (int(screen_size[0] * COMMAND_BUTTONS["HP"][0]), int(screen_size[1] * COMMAND_BUTTONS["HP"][1]))
    light_kick = (int(screen_size[0] * COMMAND_BUTTONS["LK"][0]), int(screen_size[1] * COMMAND_BUTTONS["LK"][1]))
    heavy_kick = (int(screen_size[0] * COMMAND_BUTTONS["HK"][0]), int(screen_size[1] * COMMAND_BUTTONS["HK"][1]))

    # Generate a dictionary for the X & Y screen coordinates of the respective buttons during the battle.
    buttons = {
        "AF": another_force,
        "LP": light_punch,
        "HP": heavy_punch,
        "LK": light_kick,
        "HK": heavy_kick
    }

    return buttons


def start_kof_command_sequence(android_device, buttons, combo_sequence,
                               wait_time_for_another_force_s,
                               button_press_delay_s):
    """ 
        Perform the string of combos in Another Eden using taps
        based on the percentages in COMMAND_BUTTONS for (X, Y)
        screen coordinates of your device. 
        1 = LP
        2 = HP
        3 = LK
        4 = HK

        However, you must do this by first entering another force.
    """
    # Trigger Another Force by tapping the "MAX" button which should be ORANGE.
    print(">> Pressing AF/MAX button...")
    android_device.perform_tap(x=buttons["AF"][0],
                               y=buttons["AF"][1])
    
    # Wait for a few seconds for another force animation to complete:
    print(">> Waiting %s seconds for AF animation to complete." % wait_time_for_another_force_s)
    time.sleep(float(wait_time_for_another_force_s))

    # Press all the buttons necessary to perform the desired combo string.
    #print("[ANOTHER EDEN] Performing KOF Combo String = %s!" % combo_string)
    print(">> Performing KOF Command!")
    print(">> START->", end='')
    for idx, command in enumerate(combo_sequence):
        if command == 1:
            button_name="LP"
            button_to_press = buttons[button_name]
        elif command == 2:
            button_name="HP"
            button_to_press = buttons[button_name]
        elif command == 3:
            button_name="LK"
            button_to_press = buttons[button_name]
        elif command == 4:
            button_name="HK"
            button_to_press = buttons[button_name]
        else:
            # This should effectively do nothing, if command is anything else.
            button_name = "N/A"
            button_to_press = buttons["AF"]

        # Tap on the respective button via X & Y screen coordinates.
        print("%s->" % button_name, end='')
        android_device.perform_tap(x=button_to_press[0], 
                                   y=button_to_press[1])
        
        # Only add a delay if this is not the last action in the sequence
        if idx < (len(combo_sequence) - 1):
            # Add some delay for the button press.
            time.sleep(float(button_press_delay_s))

    print("END")


def generate_chain(chain_string, command_list, fighter):
    """
        Perform the logic to check the chain sequence and
        report to player if the sequence is a true chain
        or if it isn't.
    """
    invalid_chain_string_flag = False
    true_combo_flag = True

    # Obtain the list of combo list for the fighter.
    supported_combos = command_list[fighter.lower()]
    
    # Process each character as a map to the actual key in the command list for the fighter.
    chain_sequence = []
    for character in chain_string:
        if character.lower() == "s":
            chain_sequence.append("super")
        
        elif character in ["1", "2", "3"]:
            chain_sequence.append("combo" + character.lower())

        else:
            print(">> [ERROR] The chain ( %s ) contains invalid characters! [supported = 1,2,3,S]" % chain_string)
            invalid_chain_string_flag = True

    # After obtaining list of command keys matching command list, check each sequence to
    # verify that the list of commands form a true chain!
    previous_combo_sequence = []
    chained_sequence = []
    for idx, combo_name in enumerate(chain_sequence):
        # The combo_name is something like "combo1", or "super" from YAML file.
        combo_sequence = supported_combos[combo_name]

        # Only on the second loop onwards, perform the logic check for the
        # true combo
        if idx > 0:
            # ie. 1,2,3 or 4
            last_action_of_previous_combo = previous_combo_sequence[-1]
            first_action_of_next_combo = combo_sequence[0]

            # A true combo is such that the previous combo last action and
            # the next combo first action are the same.
            if last_action_of_previous_combo == first_action_of_next_combo:
                # Since this is a true combo, you can remove the duplicate action
                # in the first index of the combo sequence and append the chain.
                combo_sequence = combo_sequence[1:]
            
            else:
                # Set a marker that the combo isn't true, but keep contin
                true_combo_flag = False
    
        # Set the current combo sequence to be the previous combo sequence
        # to check on the next loop.
        previous_combo_sequence = combo_sequence

        # Continue to append the actual combo sequence.
        chained_sequence.extend(combo_sequence)
    
    return invalid_chain_string_flag, true_combo_flag, chained_sequence


def kof_battler_cli(android_device, buttons, command_list,
                    wait_time_for_another_force_s,
                    button_press_delay_s):
    """
        Basically a CLI Menu for user to specify desired commands
        into the KOF battle after reading either a:
            ORANGE BAR = Another Force/MAX is ready for combos
            BLUE BAR = Can perform Super

        The CLI doesn't know whether super is ready or not, so
        the user must use their own judgement to correctly
        perform the actions to perform the desired combos.

        REQUIREMENTS:
            - Must be your turn
            - Must have orange bar.
            - For super moves, make sure you have full bar
    """
    # The fighters are the list of names in 
    supported_fighters = list(command_list.keys())

    print("=====================================================")
    print("----- KOF Battle CLI Interface")
    print("=====================================================")

    while(True):
        # Request the user to select a fighter.
        # TODO: Allow quitting?
        fighter = input("--> Please specify the fighter (%s): " % supported_fighters)
        if fighter.lower() in supported_fighters:
            print(">> SELECTED FIGHTER =  [ %s ]" % fighter.lower())
        else:
            continue

        while(True):
            # Now select the support combos for the fighter
            supported_commands = list(command_list[fighter.lower()].keys())

            # Add Chaining to the supported commands
            supported_commands.append("chain")

            print(">> COMMAND LIST: %s" % supported_commands)

            command_to_perform = input("--> Please specify the command: ")
            if command_to_perform in supported_commands:
                print(">>> Performing command: [ %s ]" % command_to_perform)
            else:
                continue

            # Obtain the list of button presses for the desired combo name.
            if command_to_perform.lower() == "chain":
                while(True):
                    chained_sequence = []

                    # To chain, input a seqence of of characters that represent the chain
                    # to perform. For example: 121 = combo1 + combo2 + combo3
                    chain_string = input("--> Enter the Chain Sequence (ie. 1,2,3, or S w/out spaces): ")
                    invalid_string_flag, true_combo_flag, chained_sequence = generate_chain(chain_string=chain_string.replace(" ", ""),
                                command_list=command_list, fighter=fighter)
                
                    # Set the current combo sequence to the chained sequence.
                    combo_sequence = chained_sequence

                    # Repeat the same loop endlessly until a correct chained sequence is provided.
                    if invalid_string_flag:
                        continue
                    
                    # In the case a non-true combo is detected, allow the user to still use it
                    # if the want.
                    if not true_combo_flag:
                        accept_non_true_combo_YesNo = input("--> The Chain you provided is NOT a true combo! Do you still want to continue? ")
                        if accept_non_true_combo_YesNo.lower() == "y" or accept_non_true_combo_YesNo.lower() == "yes":
                            break
                        else:
                            # Repeat the previous prompt again to change the chain sequence input.
                            continue
                    else:
                        # On true_combo_flag being true, also end the repeated chain sequence input loop.
                        break
            else:
                combo_sequence = command_list[fighter.lower()][command_to_perform.lower()]

            # Perform the button presses for the combo.
            start_kof_command_sequence(android_device=android_device,
                                       buttons=buttons,
                                       combo_sequence=combo_sequence,
                                       wait_time_for_another_force_s=wait_time_for_another_force_s,
                                       button_press_delay_s=button_press_delay_s)
            
            # After the command finishes, prompt user if they want to continue to use
            # the same fighter, or change the figher.
            change_fighter_YesNo = input("--> Change fighter? ")
            if change_fighter_YesNo.lower() == "y" or change_fighter_YesNo.lower() == "yes":
                break
            else:
                continue
            

def run_android_macros(args):
    """ Runs device series of macros for your Another Eden. """

    # Open the YAML config file for the KOF Symphony command list
    kof_commands_list = {}
    with open(YAML_FILE, 'r') as file:
        kof_commands_list = yaml.safe_load(file)

    # Connect to the Android Device and obtain the handle. 
    android_device = obtain_device_configuration(args)

    # Obtain the screen size (which will be used for taps and swipes)
    screen_size = android_device.get_screen_resolution()

    # Display the time out parameters.
    print("[ANOTHER EDEN] AF wait time = %s seconds, Button press time = %s seconds." % (
        args.another_force_wait_time,
        args.button_press_click_time))

    # Obtain the coordinates of the buttons for KOF Symphony battles
    command_buttons = obtain_kof_battle_buttons(screen_size)

    # Loop a menu here where the user specifies the following:
    # Name of the fighter, the command to perform, or a chain.
    # TODO: Allow chaining series of combos like 123S or 2321
    kof_battler_cli(android_device, command_buttons, kof_commands_list,
                    wait_time_for_another_force_s=args.another_force_wait_time,
                    button_press_delay_s=args.button_press_click_time)
    

# Use parser for the help menu and to return as args to the main function..
parser = argparse.ArgumentParser(prog='ANOTHER EDEN KOF Symphony Battler Script', description='Runs desired sequence of Android macros for your connected android device for the ANOTHER EDEN mobile game.')
parser.add_argument("--serial_number", "-s", action='store', type=str, required=True, help='Serial Number of Android device as seen by adb')
parser.add_argument("--another_force_wait_time", action='store', type=float, default=1.5, required=False, help='Time delay to wait for AF animation to finish.')
parser.add_argument("--button_press_click_time", action='store', type=float, default=0.75, required=False, help='Time delay to wait for AF animation to finish.')
parser.add_argument("--verbose", action='store_true', help='Shows raw command output.')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
args = parser.parse_args()
run_android_macros(args)