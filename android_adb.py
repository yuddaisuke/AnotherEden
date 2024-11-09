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

   Library Description:
        A simple class which runs adb commands automatically via subprocess

   Usage:
   -------------
   <put something here>
"""
import datetime
import subprocess
import time


class __OSEssentials(object):
    """ OS Essential commands for logging and control """
    def _get_pc_time(self):
        """ Returns the PC time as a datetime string. """
        return datetime.datetime.now()


class AndroidUSB(__OSEssentials):
    """ Class which communicates with the Android device via USB."""

    manufacturer = None
    serial_number = None
    model = None
    image_version = None
    screen_resolution = None
    screen_orientation = None

    _supported_events = {"back": "KEYCODE_BACK",
                         "menu": "KEYCODE_MENU",
                         "home": "KEYCODE_HOME",
                         "mute_volume": "KEYCODE_MUTE",
                         "vol_up": "KEYCODE_VOLUME_UP",
                         "vol_down": "KEYCODE_VOLUME_DOWN",
                         "pause": "KEYCODE_MEDIA_PLAY_PAUSE",
                         "stop_playback": "KEYCODE_MEDIA_STOP",
                         "wakeup": "KEYCODE_WAKEUP",
                         "lock": "KEYCODE_SOFT_SLEEP",
                         "end_call": "KEYCODE_ENDCALL"}

    def __init__(self, device_sn, restart_device=False):
        """ Initialize the the class to get basic info on the connected device, and this assumes drivers are already installed and user has tested it. """

        # The Phone Serial is automatically passed by the user.
        self.serial_number = device_sn

        # If restart_device is enabled, kill the adb server and the restart it with 'adb devices' command.
        if restart_device:
            print("[ %s ] >> [ANDROID] Restart ADB and hopefully connecting to the Android Device = %s." % (self._get_pc_time(), self.serial_number))
            self._kill_server()
            self._startup()

        # Collect some basic information about the device.
        print("[ %s ] >> [ANDROID] Pulling basic system information about the device..." % self._get_pc_time())
        self._get_basic_info()

        # Print out relevant information.
        self._check_screen_resolution()
        print("[ %s ] >> [ANDROID] Found additional information:\n" % self._get_pc_time())
        print("\t\tScreen Resolution (x,y): (%s,%s)\n" % (self.screen_resolution[0], self.screen_resolution[1]))
        
    def _kill_server(self):
        """ Kills the current adb server running in the background. """
        self._command = "adb kill-server"

        # Run the command in shell and output the command to stdout
        output = subprocess.run(self._command, shell=True, capture_output=True, text=True)

        # Return only the command execution output
        return output.stdout

    def _startup(self):
        """ Launches adb device command. """
        self._command = "adb devices"

        # Run the command in shell and output the command to stdout
        output = subprocess.run(self._command, shell=True, capture_output=True, text=True)

        # Return only the command execution output
        return output.stdout

    def _send_command(self, command, with_parsable_output=False, print_command=False):
        """ Sends command to the adb device with given serial number. """
        self._command = "adb -s {device_sn} {command}".format(device_sn=self.serial_number, command=command)
        if print_command:
            print("[ %s ] >> [ANDROID] Sending command: %s" % (self._get_pc_time(), self._command))

        if not with_parsable_output:
            output = subprocess.run(self._command, shell=True, capture_output=True, text=True)

            # Return only the command execution output as list of characters.
            return output.stdout
        else:
            adb_process = subprocess.Popen(self._command, shell=True, text=True, stdout=subprocess.PIPE)
            return self._read_output_as_lines(process=adb_process)

    def _read_output_as_lines(self, process):
        """ Reads through subprocess output and returns data as a list. """
        lines = []
        while True:
            line = process.stdout.readline()
            if not line:
                break
            else:
                lines.append(line.strip())
        return lines

    def _getprop_line_data(self, line):
        """ Returns value of a getprop entry. """
        return line.split("]: [")[-1].split("]")[0].strip()

    def root_and_remount(self, command):
        """ 
           Performs Root and Remount on the device.
        """
        root_cmd = "root"
        remount_cmd = "remount"
        _ = self._send_command(command=root_cmd)
        _ = self._send_command(command=remount_cmd)

    def _get_basic_info(self):
        """ 
            Obtains basic information about the device.
                - Phone Manufacturer
                - Phone Model
                - Phone SW version
        """
        command_to_send = "shell getprop"

        # Return the output of getprop
        result_as_lines = self._send_command(command=command_to_send, with_parsable_output=True, print_command=True)
        
        # Parse throught the lines for the desired fields matching the substrings:
        phone_sw_version_build_version = ""
        phone_sw_version_build_number = ""
        phone_model = ""
        phone_id_name = ""
        for line in result_as_lines:
            if line.find("ro.vendor.build.id") >= 0:
                phone_sw_version_build_version = self._getprop_line_data(line)
            elif line.find("ro.vendor.build.version.incremental") >= 0:
                phone_sw_version_build_number = self._getprop_line_data(line)
            elif line.find("ro.product.manufacturer") >= 0:
                self.manufacturer = self._getprop_line_data(line)
            elif line.find("ro.product.model") >= 0:
                phone_model = self._getprop_line_data(line)       
            elif line.find("ro.product.model") >= 0:
                phone_model = self._getprop_line_data(line)     
            elif line.find("ro.product.name") >= 0:
                phone_id_name = self._getprop_line_data(line)

        # After parsing the desired output, combine build_version and number for phone_sw_version
        self.image_version = phone_sw_version_build_version + " (%s)" % phone_sw_version_build_number
        self.model = phone_id_name + " (%s)" % (phone_model)

        # Print out relevant information.
        print("[ %s ] >> [ANDROID] Found device information\n" % self._get_pc_time())
        print("\t\tManufacturer: %s" % self.manufacturer)
        print("\t\tModel: %s" % self.model)
        print("\t\tSerial Number: %s" % self.serial_number)
        print("\t\tImage Version: %s" % self.image_version)

    def _check_screen_orientation(self):
        """ Returns whether the screen is in Portrait or Landscape Mode. """
        command_to_send = "shell dumpsys input"
        result_as_lines = self._send_command(command=command_to_send, with_parsable_output=True)

        for line in result_as_lines:
            if line.find("Viewport INTERNAL") >= 0:
                orientation = int(line.split(", orientation=")[-1].split(",")[0].strip())

                # 0 = portrait, 1 = landscape
                if orientation == 0:
                    self.screen_orientation="portrait"
                else:
                    # orientation == 1
                    self.screen_orientation="landscape"

    def get_screen_orientation(self):
        """ Checks the current screen orientation. """
        self._check_screen_orientation()
        print("[ %s ] >> [ANDROID] Screen Orientation = %s." % (self._get_pc_time(), self.screen_orientation.upper()))

        return self.screen_orientation

    def _check_screen_resolution(self):
        """ Obtains the screen resolution of the display with dumpys output. """
        command_to_send = "shell dumpsys window"
        result_as_lines = self._send_command(command=command_to_send, with_parsable_output=True)

        # Look for line containing display information and then stop searching.
        screen_x=0
        screen_y=0
        for line in result_as_lines:
            if line.find("mDisplayFrame") >= 0:
                screen_coordinates = line.split(" - ")[-1].strip().split(")")[0].split(", ")
                ref_screen_coord_1 = int(screen_coordinates[0].strip())
                ref_screen_coord_2 = int(screen_coordinates[1].strip())

                if ref_screen_coord_1 < ref_screen_coord_2:
                    if self.screen_orientation == "landscape":
                        screen_x = ref_screen_coord_2
                        screen_y = ref_screen_coord_1
                    else:
                        screen_x = ref_screen_coord_1
                        screen_y = ref_screen_coord_2
                else:
                    if self.screen_orientation == "landscape":
                        screen_x = ref_screen_coord_1
                        screen_y = ref_screen_coord_2
                    else:  
                        screen_x = ref_screen_coord_2
                        screen_y = ref_screen_coord_1         
                break
        
        self.screen_resolution = (screen_x, screen_y)

    def get_screen_resolution(self):
        # Check screen orientation.
        self._check_screen_orientation()
        print("[ %s ] >> [ANDROID] Screen Orientation = %s." % (self._get_pc_time(), self.screen_orientation.upper()))

        # Check the screen resolution parameters.
        self._check_screen_resolution()
        print("[ %s ] >> [ANDROID] Screen Size = (X,Y) = (%s, %s)." % (self._get_pc_time(), self.screen_resolution[0], self.screen_resolution[1]))
        
        return self.screen_resolution

    def send_keycode(self, keycode_string):
        """ Sends a keycode event """
        command_to_send = "shell input keyevent {keycode}".format(keycode=keycode_string)
        _ = self._send_command(command=command_to_send, print_command=True)

    def send_event(self, supported_event):
        """ Sends a keycode as an event name that is supported """
        supported_events = list(self._supported_events.keys())
        if supported_event in supported_events:
            self.send_keycode(self._supported_events[supported_event])
        else:
            print("The event=%s, is not supported! (SUPPORTED=%s)" % (supported_event, supported_events))

    def perform_tap(self, x, y, repeat_count=1, repeat_interval_ms=1000):
        """ Perform a tap to the given X and Y coordinate repeatedly based on repeat_count value at an interval of repeat_interval_ms (milliseconds). """
        if (x <= self.screen_resolution[0] and y<= self.screen_resolution[1]):
            for loop_number in range(repeat_count):
                print("[ %s ] >> [ANDROID] Performing Screen tap at (X,Y) = (%s,%s)." % (self._get_pc_time(), x, y))
                command_to_send = "shell input tap {x} {y}".format(x=x, y=y)
                _ = self._send_command(command=command_to_send, print_command=True)

                if (repeat_count > 1 and loop_number < (repeat_count - 1)):
                    print("[ %s ] >> [ANDROID] Waiting %s ms before tapping screen again." % (self._get_pc_time(), repeat_interval_ms))
                    time.sleep(repeat_interval_ms / 1000)
        else:
            print("[ %s ] >> [ANDROID] Error, the X & Y coordinate (%s,%s) given are out of range!" % (self._get_pc_time(), x, y))

    def perform_swipe(self, coord1, coord2, length_ms=3000):
        """ Perform a swipe for length_ms (milliseconds) from coord1 (x1,y1) to coord2 (x2,y2) """
        if (coord1[0] <= self.screen_resolution[0] and coord1[1]<= self.screen_resolution[1]) and (coord2[0] <= self.screen_resolution[0] and coord2[1]<= self.screen_resolution[1]):
            print("[ %s ] >> [ANDROID] Performing Swipe from (%s,%s) to (%s, %s)" % (self._get_pc_time(), coord1[0], coord1[1], coord2[0], coord2[1]))
            command_to_send = "shell input swipe {x1} {y1} {x2} {y2} {duration_ms}".format(x1=coord1[0],
                                                                                           y1=coord1[1],
                                                                                           x2=coord2[0],
                                                                                           y2=coord2[1],
                                                                                           duration_ms=length_ms)
            _ = self._send_command(command=command_to_send, print_command=True)
        else:
            print("[ %s ] >> [ANDROID] Error, One or more X & Y coordinate given are out of range!" % (self._get_pc_time()))

    def type_text(self, text):
        """ Types some text on the screen. """
        print("[ %s ] >> [ANDROID] Sending text: %s" % (self._get_pc_time(), text))
        text_for_android_cmd = text.replace(" ", "%s")

        command_to_send = 'shell input text "{text}"'.format(text=text_for_android_cmd)
        _ = self._send_command(command=command_to_send, print_command=True)

    def take_screenshot(self, name):
        """ Takes a screenshot on the Android phone. """
        image_file = "/sdcard/Pictures/" + name
        print("[ %s ] >> [ANDROID] Taking Screenshot." % (self._get_pc_time()))
        
        command_to_send = 'shell screencap {image_file}'.format(image_file=image_file)
        _ = self._send_command(command=command_to_send, print_command=True)

    def pop_screenshot(self, name, output_location):
        """ Pulls the screenshot from the Android phone and then removes it from the phone. """
        image_file = "/sdcard/Pictures/" + name

        print("[ %s ] >> [ANDROID] Pulling image file: %s" % (self._get_pc_time(), image_file))
        command_to_send = 'pull {image_file} {output_location}'.format(image_file=image_file, output_location=output_location)
        _ = self._send_command(command=command_to_send, print_command=True)

        print("[ %s ] >> [ANDROID] Removing image file: %s" % (self._get_pc_time(), image_file))
        command_to_send = 'shell "rm {image_file}"'.format(image_file=image_file)
        _ = self._send_command(command=command_to_send, print_command=True)

    def TearDown(self):
        """Closes the connection to the device."""
        self.DEVICE.reset()
        # Do something.