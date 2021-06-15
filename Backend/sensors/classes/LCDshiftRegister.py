from classes.ShiftRegisterClass import ShiftRegister
from classes.LCDClass import LCDclass

class LCD_ShiftRegister(LCDclass):

    def __init__(self, datapins=[16,12,25,24,23,26,19,13], enablepin=21, registerselectpin=18):
        super().__init__(datapins, enablepin, registerselectpin) # init LCD class
        self.shreg = ShiftRegister() # init ShiftRegister class
        self.shreg.reset_shift_register() # reset

    
    def set_data_bits(self, byte):
        self.shreg.write_byte(byte) # load byte
        self.shreg.copy_to_storage_register() # write byte
        self.shreg.output_enabled = True # ensure output is enabled
    
    def init_LCD(self):
        # function set
        self.send_instruction(0x38) #0b0011 1000
        # display on but cursor and blink off
        self.send_instruction(0x0c) # 0b0000 1100
        # clear display & cursor home
        self.send_instruction(0x01) #0b0000 0001
