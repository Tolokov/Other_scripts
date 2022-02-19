import tkinter as tk
from tkinter.messagebox import showinfo

from random import randrange


class Map(tk.Button):

    def __init__(self, master, row, column, num, *args, **kwargs):
        super(Map, self).__init__(master, *args, **kwargs)
        self.fields_row = row
        self.fields_column = column
        self.num = num
        self.course = None
        self.is_head = False
        self.is_snake = False
        self.is_apple = False
        self.live = 0

    def __repr__(self):
        return f'{self.fields_row}, {self.fields_column}'


class ControlButtons(tk.Button):

    def __init__(self, master, text, command, *args, **kwargs):
        super(ControlButtons, self).__init__(master, *args, **kwargs)
        self.btn = tk.Button(foreground="#ccc", font="15", relief=tk.GROOVE, text=text, command=command)
        self.btn.place(anchor="center", height=60, width=80)

        if text == 'UP':
            self.btn.place(relx=.77, rely=.26)
        elif text == 'DOWN':
            self.btn.place(relx=.77, rely=.54)
        elif text == 'LEFT':
            self.btn.place(relx=.66, rely=.4)
        else:
            self.btn.place(relx=.88, rely=.4)


class Snake:

    WINDOW = tk.Tk()
    WINDOW.title('Snake')
    WINDOW.geometry("800x500+470+240")
    WINDOW.resizable(False, False)
    WINDOW.iconbitmap('report_ru_blacklist\\images\\other_images\\favicon.ico')

    SCORE = 0
    IS_GAME_OVER = False
    DEBUG = False

    def __init__(self):
        """Window initialization"""
        self.map = []
        self.seconds = 0
        self.minutes = 0
        self.up = None
        self.down = None
        self.left = None
        self.right = None
        self.rating = None
        self.previous_course = 'right'
        self.is_action = False
        self.columns = 16
        self.rows = 17

    def register_control_buttons(self):
        self.up = self.create_control_buttons('up')
        self.down = self.create_control_buttons('down')
        self.left = self.create_control_buttons('left')
        self.right = self.create_control_buttons('right')

        self.WINDOW.bind("<Up>", lambda move: self.user_action('up'))
        self.WINDOW.bind("<W>", lambda move: self.user_action('up'))
        self.WINDOW.bind("<w>", lambda move: self.user_action('up'))

        self.WINDOW.bind("<Down>", lambda move: self.user_action('down'))
        self.WINDOW.bind("<S>", lambda move: self.user_action('down'))
        self.WINDOW.bind("<s>", lambda move: self.user_action('down'))

        self.WINDOW.bind("<Left>", lambda move: self.user_action('left'))
        self.WINDOW.bind("<A>", lambda move: self.user_action('left'))
        self.WINDOW.bind("<a>", lambda move: self.user_action('left'))

        self.WINDOW.bind("<Right>", lambda move: self.user_action('right'))
        self.WINDOW.bind("<D>", lambda move: self.user_action('right'))
        self.WINDOW.bind("<d>", lambda move: self.user_action('right'))

        self.rating = tk.Button(foreground="#ccc", font="15", relief=tk.GROOVE, text='0')
        self.rating.place(anchor="center", height=60, width=80, relx=.77, rely=.4)
        self.rating['state'] = 'disabled'

    def create_control_buttons(self, course: str):
        return ControlButtons(master=self.WINDOW, text=course.upper(), command=lambda: self.user_action(course.lower()))

    def create_map(self):
        number = 0
        for row in range(1, int(self.rows) + 1):
            line = []
            for column in range(1, int(self.columns) + 1):
                number += 1
                btn = Map(Snake.WINDOW, row=row, column=column, width=2, num=number, relief=tk.GROOVE, borderwidth=2)
                btn.grid(row=row, column=column, stick='NWES')
                if self.DEBUG:
                    # btn['text'] = f'{row}:{column}'
                    btn['text'] = number
                line.append(btn)
            self.map.append(line)

    def create_border(self):
        """Upgrade visual, is new label column number 0"""
        border = tk.Label(width=6)
        border.grid(row=0, column=0)

    def update_clock(self):
        """cycle"""
        self.seconds += 1
        if self.seconds == 60:
            self.seconds = 0
            self.minutes += 1
        timer = tk.Label(text='{:02d}:{:02d}'.format(self.minutes, self.seconds), font="15", relief=tk.SOLID)
        timer.place(relx=.77, rely=.8, anchor="center", height=60, width=80)
        self._auto_move()
        self.WINDOW.after(1000, self.update_clock)

    def _auto_move(self):
        """When the user is idle, the movement is triggered"""
        if not self.is_action:
            self.move(self.previous_course)
        if self.is_action:
            self.is_action = False

    def set_head(self, btn_head, course):
        if self.DEBUG:
            btn_head['text'] = 'H'
        btn_head['bg'] = '#7BE36D'
        btn_head.is_head = True
        btn_head.course = course

    def remove_head(self, btn_head):
        if self.DEBUG:
            btn_head['text'] = 'D'
            btn_head['bg'] = 'yellow'
        btn_head.is_head = False
        btn_head.is_snake = True
        btn_head.live = 2

    def set_tail(self, btn_tail):
        if self.DEBUG:
            btn_tail['text'] = 't'
        btn_tail['bg'] = '#A8E4A0'
        btn_tail.is_snake = True

    @staticmethod
    def remove_tail(btn_tail):
        btn_tail.is_snake = False
        btn_tail['text'] = ''
        btn_tail['bg'] = 'white'
        btn_tail.live = 0

    def create_snake(self):
        """Create a player, default head 137 and tail 136."""
        head = self.map[int(self.columns / 2)][int(self.rows / 2)]
        tail = self.map[int(self.columns / 2)][int(self.rows / 2) - 1]
        self.set_head(head, 'right')
        self.set_tail(tail)
        tail.live = 1

    def create_apple(self):
        """Choose a random number on the map that is not currently a snake"""
        btn = self.get_random_field()
        debug_count = 0
        while btn.is_snake or btn.is_head:
            btn = self.get_random_field()
            debug_count += 1
            if debug_count > self.columns * self.rows:
                self.game_win()
                break
        btn.is_apple = True
        if self.DEBUG:
            btn['text'] = 'X'
        btn['bg'] = '#E15668'

    def get_random_field(self):
        return self.map[randrange(0, self.rows)][randrange(0, self.columns)]

    def _check_head(self):
        """HEAD search, if HEAD is not found then game over"""
        search_head = 0
        for line in self.map:
            for btn in line:
                search_head += 1
                if btn.is_head:
                    break
            if btn.is_head:
                break
            if search_head > self.columns * self.rows:
                self.game_over('HEAD IS LOST')
        return btn

    def _move(self, course, where_a_head_in_row, where_a_head_in_column):
        """
        Basic movement func.

        Due to the create_border func, the offset is inaccurate. _move function does not contain this problem.
        """
        match course:
            case 'right':
                if where_a_head_in_column >= self.columns:
                    where_a_head_in_column = 0
                self.set_head(self.map[where_a_head_in_row - 1][where_a_head_in_column], course)
            case 'left':
                self.set_head(self.map[where_a_head_in_row - 1][where_a_head_in_column - 2], course)
            case 'up':
                self.set_head(self.map[where_a_head_in_row - 2][where_a_head_in_column - 1], course)
            case 'down':
                if where_a_head_in_row >= self.rows:
                    where_a_head_in_row = 0
                self.set_head(self.map[where_a_head_in_row][where_a_head_in_column - 1], course)
            case _:
                print('Unknown course')

    def user_action(self, course):
        """Checking who initiated the action, the user or the _auto_move method"""
        self.is_action = True
        self.move(course)

    def move(self, course):
        try:
            head = self._check_head()
            if self.IS_GAME_OVER == False:
                if self.if_course_not_is_back(course):
                    self.remove_head(head)
                    self.set_tail(head)
                    self._move(course, head.fields_row, head.fields_column)
                    self.check_progress_status()
        except UnboundLocalError as u:
            self.map = []
            self.reload()
            print(u)

    def eat_apple(self, btn):
        btn.is_apple = False
        self.SCORE -= 1
        self.rating['text'] = self.SCORE * -1

    def game_win(self):
        self.IS_GAME_OVER = True
        self.WINDOW.quit()
        showinfo(f'Congratulations! You win!', 'Time : {:02d}:{:02d}'.format(self.minutes, self.seconds))

    def game_over(self, message):
        self.IS_GAME_OVER = True
        print(f'Game over!!!\n{message}')
        showinfo(f'Unfortunately you lost!', message)

    def if_collision(self, btn):
        """Check for defeat. Protection from death if the length of the snake is less than three cells"""
        if btn.is_head and btn.is_snake and self.SCORE < -2:
            if self.DEBUG:
                print(btn.live)
            self.game_over('YOU ATE YOURSELF')

    def if_course_not_is_back(self, course):
        """Self-eating protection"""
        match self.previous_course + ',' + course:
            case 'right,left':
                return False
            case 'left,right':
                return False
            case 'up,down':
                return False
            case 'down,up':
                return False
            case _:
                self.previous_course = course
                return True

    def if_win(self):
        if self.SCORE * -1 >= (self.columns * self.rows) - 2:
            self.game_win()

    def check_progress_status(self):
        """Trigger all events"""
        for line in self.map:
            for btn in line:
                self.if_collision(btn)

                if btn.is_head and btn.is_apple:
                    self.eat_apple(btn)
                    self.if_win()
                    self.create_apple()

                elif btn.is_snake and not btn.is_head:
                    btn.live -= 1
                    if btn.live < self.SCORE + 1:
                        self.remove_tail(btn)

            if self.IS_GAME_OVER:
                break

    def debug_activate(self):
        self.DEBUG = True
        self.reload()

    def create_menu(self):
        menu = tk.Menu(self.WINDOW)
        self.WINDOW.config(menu=menu)

        settings_menu = tk.Menu(menu, tearoff=0)
        settings_menu.add_command(label='New game', command=self.reload)
        settings_menu.add_command(label='Settings', command=self.settings)
        settings_menu.add_command(label='DEBUG', command=self.debug_activate)
        settings_menu.add_cascade(label='Exit', command=self.WINDOW.quit)
        menu.add_cascade(label='Menu', menu=settings_menu)

    def reload(self):
        self.IS_GAME_OVER = False
        self.minutes = 0
        self.seconds = 0
        self.SCORE = 0
        for line in self.map:
            for btn in line:
                btn.destroy()
        self.map = []
        self.create_widgets()
        self.register_control_buttons()

    def settings(self):
        self.is_action = True

        settings_window = tk.Toplevel(self.WINDOW)
        settings_window.wm_title('Settings')

        tk.Label(settings_window, text='Number of rows').grid(row=0, column=0)
        row = tk.Entry(settings_window)
        row.grid(row=0, column=1, padx=20, pady=20)
        row.insert(0, self.rows)

        tk.Label(settings_window, text='Number of columns').grid(row=1, column=0)
        column = tk.Entry(settings_window)
        column.grid(row=1, column=1, padx=20, pady=20)
        column.insert(0, self.columns)

        btn_save = tk.Button(
            settings_window,
            text='Save',
            command=lambda: self.save_change(settings_window, row, column))
        btn_save.grid(row=2, column=0, columnspan=2)

    def save_change(self, window,  row, column):
        try:
            self.rows = int(row.get())
            if self.rows <= 3:
                self.rows = 3
            self.columns = int(column.get())
            if self.columns <= 3:
                self.columns = 3
            if self.columns * self.rows > 300:
                self.WINDOW.geometry(f"{int(self.rows * 6)}0x{int(self.columns * 3)}0+470+240")

        except ValueError as ve:
            self.rows = 16
            self.columns = 17
            print(ve)
        except Exception as e:
            self.rows = 16
            self.columns = 17
            print(e)
        finally:
            window.destroy()
            self.reload()

    def create_widgets(self):
        """Creation of the main objects of the application window. Menu, Indent, Map, Player, Target"""
        self.create_menu()
        self.create_border()
        self.create_map()
        self.create_snake()
        self.create_apple()

    def start(self):
        """Creating control buttons, starting a time counter, creating a game loop"""
        self.create_widgets()
        self.update_clock()
        self.register_control_buttons()
        self.WINDOW.mainloop()


def main():
    game = Snake()
    game.start()


if __name__ == '__main__':
    main()
