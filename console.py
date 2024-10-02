import asyncio
from pyreadline3 import Readline


async def break_console(user_input: str = ""):
    return True


class CommandLine:
    def __init__(self, input_text: str = "User input:", commands: dict = None, debug_mode: bool = False):
        """
        :param input_text: --> Prompt start-witch text
        :param commands:   --> Default terminal commands ("exit" is default command for turn off terminal)
        :param debug_mode: --> Turn off/on debug mode
        """
        self.is_input = False
        if commands is None:
            self.commands = {"exit": break_console}
        else:
            self.commands = commands
        self.input_text = input_text

        self.debug_mode = debug_mode
        self.readline = Readline()
        self._prompt = ""

    def add_command(self, command_name, command):
        self.commands[command_name] = command

    def del_command(self, command):
        del self.commands[command]

    def log(self, *args, **kwargs):
        """prints text safely to input"""
        print("\r" + " " * (len(self._prompt) + len(self.readline.get_line_buffer())) + "\r", end="")
        print(*args, **kwargs)
        text = (self._prompt if not self.is_input else self._prompt.replace(self.input_text, ""))
        print(text + self.readline.get_line_buffer(), end="", flush=True)

    async def async_input(self, prompt: str):
        self._prompt = prompt
        return await asyncio.to_thread(input, prompt)

    async def input_loop(self):
        run = True
        while run:
            user_input = await self.async_input(self.input_text)
            self.is_input = True
            if self.debug_mode:
                print("input command: ", user_input)

            for command_name in self.commands:
                if user_input.startswith(command_name):
                    if self.debug_mode:
                        print(f"command: [{command_name}] running")
                    if not isinstance(self.commands[command_name], list):
                        call_ = await self.commands[command_name](user_input)
                        if call_ is True:
                            run = False
                    else:
                        calls_ = [await command(user_input) for command in self.commands[command_name]]
                        if all(calls_):
                            run = False
                    self.is_input = False
