import struct
import sys

import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtNetwork import QHostAddress, QUdpSocket
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDial,
                             QFormLayout, QLabel, QLineEdit, QPushButton,
                             QWidget)

from gf import get_gf, get_sig


class CustomLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def text(self):
        text = super().text()
        return text if text and text != '-' else '0'


class SenderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.start_byte = '0x24'
        self.statuses = ['0x01', '0x02', '0x04', '0x08', '0x10']
        self.num_packet = 1
        self.sended_packets = 0
        self.ip_adress = QHostAddress.SpecialAddress.LocalHost
        self.udp_port = 9001
        self.udp_socket = QUdpSocket(self)
        self.udp_socket.connectToHost(self.ip_adress, self.udp_port)
        self.send_timer = QTimer()
        self.send_timer.timeout.connect(self.send_data)
        self.packets_in_seconds = 1

        self.initUI()

    def initUI(self):
        main_layout = QFormLayout()

        start_byte_label = QLabel('Стартовая последовательность: ')
        self.start_byte_line_edit = CustomLineEdit(self.start_byte)
        main_layout.addRow(start_byte_label, self.start_byte_line_edit)

        status_label = QLabel('Статус: ')
        self.status_combo_box = QComboBox()
        self.status_combo_box.addItems(self.statuses)
        main_layout.addRow(status_label, self.status_combo_box)

        null_label = QLabel('Нулевое значение: ')
        self.null_line_edit = CustomLineEdit('0')
        main_layout.addRow(null_label, self.null_line_edit)

        compas_x_label = QLabel('Компас Х: ')
        self.compas_x_line_edit = CustomLineEdit('0')
        main_layout.addRow(compas_x_label, self.compas_x_line_edit)

        compas_y_label = QLabel('Компас Y: ')
        self.compas_y_line_edit = CustomLineEdit('0')
        main_layout.addRow(compas_y_label, self.compas_y_line_edit)

        pressure_label = QLabel('Давление: ')
        self.pressure_line_edit = CustomLineEdit('0')
        main_layout.addRow(pressure_label, self.pressure_line_edit)

        temp_keller_label = QLabel('Температура Keller: ')
        self.temp_keller_line_edit = CustomLineEdit('0')
        main_layout.addRow(temp_keller_label, self.temp_keller_line_edit)

        temp_rtd_label = QLabel('Температура RTD: ')
        self.temp_rtd_line_edit = CustomLineEdit('0')
        main_layout.addRow(temp_rtd_label, self.temp_rtd_line_edit)

        num_packet_label = QLabel('Номер пакета: ')
        self.num_packet_line_edit = CustomLineEdit(str(self.num_packet))
        self.num_packet_line_edit.setDisabled(True)
        main_layout.addRow(num_packet_label, self.num_packet_line_edit)

        freq_label = QLabel('Частота, Гц')
        self.freq_line_edit = CustomLineEdit(str(1_000))
        main_layout.addRow(freq_label, self.freq_line_edit)

        sampling_label = QLabel('Дискретизация, Гц')
        self.sampling_line_edit = CustomLineEdit(str(32_000))
        main_layout.addRow(sampling_label, self.sampling_line_edit)

        self.angle_label = QLabel('Угол 0, град')
        self.angle_dial = QDial()
        self.angle_dial.setRange(0, 359)
        self.angle_dial.setValue(270)
        self.angle_dial.setNotchesVisible(True)
        self.angle_dial.setWrapping(True)
        self.angle_dial.valueChanged.connect(self.dial_change_event)
        main_layout.addRow(self.angle_label, self.angle_dial)

        self.random_check_box = QCheckBox('Случайные данные')
        self.random_check_box.checkStateChanged.connect(self.random_click)
        main_layout.addRow(self.random_check_box)

        self.send_button = QPushButton('Начать отправку')
        self.send_button.clicked.connect(self.toggle_send)
        main_layout.addRow(self.send_button)

        self.alarm_label = QLabel()
        main_layout.addRow(self.alarm_label)

        self.setLayout(main_layout)
        self.setWindowTitle('Отправка данных по UDP')
        self.show()

    def dial_change_event(self, value):
        self.angle_label.setText(f'Угол {(abs(360 - value) - 90) % 360}, град')

    def random_click(self):
        status = self.random_check_box.isChecked()
        for widget in [self.freq_line_edit, self.angle_dial]:
            widget.setDisabled(status)

    def toggle_send(self):
        if self.send_timer.isActive():
            self.stop_sending()
            return
        self.start_sending()

    def stop_sending(self):
        self.send_button.setText('Начать отправку')
        self.sended_packets = 0
        self.send_timer.stop()

    def start_sending(self):
        self.alarm_label.setText('')
        self.send_button.setText('Остановить отправку')
        self.send_timer.start(1000)

    def send_data(self):
        # тип данных постоянных параметров с формы на секунду
        data_format = '<B B H h h H h h'
        try:

            header = int(self.start_byte_line_edit.text(), base=16)
            status = int(self.status_combo_box.currentText(), base=16)
            null = int(self.null_line_edit.text())
            compas_x = int(self.compas_x_line_edit.text())
            compas_y = int(self.compas_y_line_edit.text())
            pressure = int(self.pressure_line_edit.text())
            temp_keller = int(self.temp_keller_line_edit.text())
            temp_rtd = int(self.temp_rtd_line_edit.text())
            sampling = int(self.sampling_line_edit.text())
            # по умолчанию диал по часовой стрелки и с 6 часов, преобразуем по формуле
            phi = int((abs(360 - self.angle_dial.value()) - 90) % 360)
            fz = int(self.freq_line_edit.text())
            if sampling < 6:
                raise ValueError
            # пакуем в байты
            fixed_data_bytes = struct.pack(
                data_format, header, status, null, compas_x, compas_y, pressure, temp_keller, temp_rtd
            )
        except:
            self.stop_sending()
            self.alarm_label.setText('Ошибка конвертации чисел')
            return

        if self.random_check_box.isChecked():
            # случайные данные, если отмечена галочка
            gf_data = np.random.randint(0, np.iinfo(
                np.int32).max, (55, 32000), dtype=np.int32)
        else:
            # высота цели
            um = 0
            # скорость звука в воде
            vt = 1500
            # получаем данные гидрофонов
            gf_data = get_sig(phi, um, fz, vt, sampling, get_gf())

        # данные батареи оставляем пустыми
        battery_data = np.array([0, 0, 0, 0, 0, 0]).astype(np.int32)
        battery_bytes = battery_data.tobytes()

        PACKET_SIZE = 6 # по описателю 
        MAX_PACKET_NUMBER = 65535  # макс инт
        
        # test1 = b''
        
        for i in range(sampling // PACKET_SIZE):
            if self.num_packet > MAX_PACKET_NUMBER:
                self.num_packet = 1
            num_packet_bytes = self.num_packet.to_bytes(2, byteorder='little')

            # данные генерируются в массиве [[0,0...0], ... [54, 54, 54...54]]
            # поэтому преобразуем по формат юдп [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1...54, 54, 54, 54, 54, 54]

            start_index = i * PACKET_SIZE
            end_index = (i + 1) * PACKET_SIZE
            COEF = 1000 # коэффициент для перевода в int32 из float
            data = (
                gf_data[:,start_index:end_index].flatten() * COEF
            ).astype(np.int32)
            data_bytes = data.tobytes()

            message = fixed_data_bytes + num_packet_bytes + data_bytes + battery_bytes
            self.udp_socket.write(message)
            self.num_packet += 1
            
            # test1 += data_bytes[24:48]

        self.num_packet_line_edit.setText(str(self.num_packet))

        self.sended_packets += int(sampling // 6)
        self.alarm_label.setText(
            f'Отправлено: {self.sended_packets} пакетов. Размер пакета: {len(message)} байт.'
        )
        
        # import matplotlib.pyplot as plt
        # plt.plot(np.frombuffer(test1, dtype=np.int32))
        # plt.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = SenderWindow()
    sys.exit(app.exec())
