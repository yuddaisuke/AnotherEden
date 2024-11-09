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
       Performs series of commands to do various tasks automatically
       in the mobile game ANOTHER EDEN on Android devices.

   Usage:
   -------------
   Supply the Android device to the command line with -s {android_sn}
"""
import android_adb as Android
import argparse
import time


def another_eden_overworld_auto_battler(args):
    """ 
        Continuously loop battles in Another Eden overworld.

        You should equip at least 5-6 increase enemy encounter grasta/badges
        on your back units, otherwise you'll need to heavily tweak this script.

        REQUIREMENTS:
            - 1 click team
            - 1 front-line unit should give 0 MP on frontline at battle start
            - No switching, kills mobs on turn 1
            - No AF
    """
    # Connect to the Android Phone.
    android_device = Android.AndroidUSB(device_sn=args.serial_number)
    
    input("================ Press ENTER to start the auto-battler ================ ")
    screen_size = android_device.get_screen_resolution()

    # based on screen-size, calculate approximate coordinates to swipe left and right.
    swipe_x1 = int(screen_size[0] * 0.25)
    swipe_x2 = int(screen_size[0] * 0.75)
    swipe_y1 = int(screen_size[1] * 0.50)
    swipe_y2 = swipe_y1
    left = (swipe_x1, swipe_y1)
    right = (swipe_x2, swipe_y2)

    # Calculate the X and Y coordinates for the Attack Button.
    tap_x = int(screen_size[0] * 0.80)
    tap_y = int(screen_size[1] * 0.80)
    
    battle_counter = 1
    while True:
        # Move from right to left 3 times
        print("[ANOTHER EDEN] Moving left and right on field 3 times...")
        android_device.perform_swipe(coord1=left, coord2=right, length_ms=3000)
        android_device.perform_swipe(coord1=right, coord2=left, length_ms=3000)
        android_device.perform_swipe(coord1=left, coord2=right, length_ms=3000)
        #android_device.perform_swipe(coord1=(277, 605), coord2=(1898, 605), length_ms=3000)
        #android_device.perform_swipe(coord1=(1898, 605), coord2=(277, 605), length_ms=3000)
        #android_device.perform_swipe(coord1=(277, 605), coord2=(1898, 605), length_ms=3000)

        # Wait a few seconds for battle to start
        print("[ANOTHER EDEN] Wait %s seconds for battle to start." % args.battle_start_time)
        time.sleep(args.battle_start_time)

        print("\n[ANOTHER EDEN] ========= STARTED OVERWORLD BATTLE # %d =========" % battle_counter)

        # Press the Attack Button
        print("[ANOTHER EDEN] Press attack button once.")
        android_device.perform_tap(x=tap_x, y=tap_y, repeat_count=2, repeat_interval_ms=1000)
        #android_device.perform_tap(x=2053, y=903, repeat_count=2, repeat_interval_ms=1000)

        # Wait a few seconds for battle to end
        print("[ANOTHER EDEN] Wait %s seconds for battle to end." % args.battle_end_time)
        time.sleep(args.battle_end_time)

        # Tap anywhere on the screen
        print("[ANOTHER EDEN] Press attack button once.")
        android_device.perform_tap(x=tap_x, y=tap_y)
        #android_device.perform_tap(x=2053, y=903)

        # Wait a few seconds to return to battlefield
        print("[ANOTHER EDEN] Wait %s seconds to return to the battlefield." % args.return_to_battlefield_time)
        time.sleep(args.return_to_battlefield_time)

        # Incrememnt the battle counter
        battle_counter +=1


def run_android_macros(args):
    """ Runs device series of macros for your application. """

    # Auto-battler that loops infinitely for overworld farming. 
    another_eden_overworld_auto_battler(args)

# Use parser for the help menu and to return as args to the main function..
parser = argparse.ArgumentParser(prog='ANOTHER EDEN Android Macro script', description='Runs desired sequence of Android macros for your connected android device for the ANOTHER EDEN mobile game.')
parser.add_argument("--serial_number", "-s", action='store', type=str, required=True, help='Serial Number of Android device as seen by adb')
parser.add_argument("--battle_start_time", action='store', type=int, required=False, default=4, help='Battle Start wait time in seconds.')
parser.add_argument("--battle_end_time", action='store', type=int, required=False, default=5, help='Battle Start wait time in seconds.')
parser.add_argument("--return_to_battlefield_time", action='store', type=int, required=False, default=4, help='Battle Start wait time in seconds.')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
args = parser.parse_args()
run_android_macros(args)