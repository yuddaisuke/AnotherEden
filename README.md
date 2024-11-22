# Another Eden Android: Battler Macro

This tool helps players on Android, automate overworld battling with their one-click-teams using adb (presumed to already be installed on their machine) as well python (3.10 or 3.11 preferred).

## PC Requirements
- Android adb tools (platform tools or Android SDK in Windows or respective installation command on Mac/Linux)
- Python 3.10 or later
- USB-debugging enabled in Developer Options on Android phone
> About-->Tap 3-5 times
> Then, Settings-->Developer Options-->USB Debugging Toggle On
- Authenticated RSA for Android device when plugged into the PC

## Overworld Battler
### How it works
Battles are relatively simple in Another Eden. Once a user enters an area that has infinite spawns (non-Hollow maps for version 1.0), they simply need to get to an area with a long strip, and from the center move left and right for a few seconds until the battle begins. Assuming that the player already has a 0 MP Unit (see [Another Eden Wiki](https://anothereden.wiki/w/Battle_start_MP_down)), presumably finishing the battle in one turn should allow battling endlessly, which is what this tool hopes to accomplish. After the battle starts, the player basically just hits attack and after a few clicks on the screen, the battle ends. This is repeated endlessly.

Here's and example of a One-click-team on the frontline (Example):
	- [0 MP First Turn] Bazette, Violet Lancer
	- [Buffer Support] Necocco AS
	- [Primary DPS w/AOE] Aldo, Tiramisu NS, Flammelapis NS, Noahxis NS, Alma AS
	- [Pain First Turn Support, or skill w/ Falcon Badge/Grasta] Suzette NS, Tsukiha ES, Chiyo AS

### In-game requirements for this to work
- Main DPS should use a 100% crit weapon (self-explanatory why)
- Have enough Pain grasta w/ respective ores on your DPS in order to do maximum AOE damage. For most battles, I've found Aldo w/ SA at a very high light (>200 light) can one shot almost any enemy at Expert/Master difficulty given the right gear and proper grastas.
- 0 MP First turn setter should use a buffer move for either PWR/INT% increase or Critical Damage increase.
- All other support should carry any grasta that can help buff the DPS unit or assist as a sub-DPS on any rare occassion enemy's resist. I find that Suzette NS's barrier pierce moves helps a lot!
- Carry Falcon Badge/Grasta to do buffs before your DPS, especially for Pain setup.
- Backline unit or units should carry at least 5-6 Enemey Encounter+ badges/ores as this will speed up how often battles are entered.

### Usage
1. First, create a virtual environment in the same directory as this project you pulled. Assuming you installed python correctly and set appropriate paths, open your Command Prompt or terminal and enter:
```
python3 -m pip venv python-venv
```
2. Plug in your phone via USB cable and run the command below. Make sure to authenticate the RSA popup prompt on your phone if the output of the command shows up as "Unathenticated" and then rerun the same command.
```
adb devices
```
3. Navigate to the Overworld are you want to run endless battles and then select your auto-battler team.
4. Navigate (via cd) to the installation folder of the python-venv. Assuming the tool files are in the same directory, run the following command:
```
# Mac/Linux
python-venv/bin/python -m overworld_battle_auto_clicker_another_eden -s <adb_serial_number>

# Windows
python-venv/Scripts/python -m overworld_battle_auto_clicker_another_eden -s <adb_serial_number>
```
5. Press ENTER when prompted to start the auto-battler.
6. Press Ctrl+C/Command+C to exit the tool. 


