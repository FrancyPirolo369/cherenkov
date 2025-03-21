import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import numpy as np
import matplotlib.pyplot as plt
from animation import simulation

class InputDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Create input fields with default values
        self.particle_speed = QLineEdit('0.9')
        self.medium_speed = QLineEdit('0.7')
        
        # Add labels and fields to layout
        layout.addWidget(QLabel('Particle Speed (as fraction of c, must be > Medium Speed):'))
        layout.addWidget(self.particle_speed)
        layout.addWidget(QLabel('Speed of Light in Medium (as fraction of c):'))
        layout.addWidget(self.medium_speed)
        
        # Add start button
        self.button = QPushButton('Start Simulation')
        self.button.clicked.connect(self.validate_and_run)
        layout.addWidget(self.button)
        
        self.setLayout(layout)
        self.setWindowTitle('Cherenkov Radiation Simulation Parameters')
        
    def validate_and_run(self):
        try:
            v_particle = float(self.particle_speed.text())
            c_medium = float(self.medium_speed.text())
            
            if not (0 < c_medium < 1 and 0 < v_particle <= 1):
                raise ValueError("Speeds must be between 0 and 1")
            if v_particle <= c_medium:
                raise ValueError("Particle speed must exceed medium light speed for Cherenkov radiation")
                
            self.hide()
            run_simulation(v_particle, c_medium)
            
        except ValueError as e:
            QMessageBox.warning(self, 'Invalid Input', str(e))
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'An error occurred: {str(e)}')

def run_simulation(v_particle, c_medium):
    simulation(v_particle, c_medium)

def main():
    app = QApplication(sys.argv)
    ex = InputDialog()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

