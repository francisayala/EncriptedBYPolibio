from sys import argv
from ui import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication
from analyze import preprocess, get_ic, FrequencyDictionary, key_search, decode, restore_from_split


class App(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)  
        self.continue_button.clicked.connect(self.do_step)
        self.change_key.clicked.connect(self.do_change_key)
        self.current_step = -1
        self.current_selected = 0
        self.freq = None
        self.step_map = [
            self.preprocess_step,
            self.ic_step,
            self.load_frequency_step,
            self.search_keys_step
        ]
    
    def do_change_key(self):
        self.current_selected = (self.current_selected + 1) % 10
        self.open_text.setPlainText(f'Ключ: {self.potential_keys[self.current_selected][0]}\n'+ \
                f' Сообщение: {restore_from_split(decode(self.potential_keys[self.current_selected][0], self.prepocessed), self.lens)}')
        self.draw_content()
    
    def draw_content(self):
        steps_content = ''
        if self.current_step >= 0:
            steps_content += f'''
                <h4>Шаг 1: предобработка текста</h4>
                Удалены пробелы и знаки препинания: <br>
                "{self.prepocessed[:30]}..."
            '''
        if self.current_step >= 1:
            concat = '''
                <h4>Шаг 2: вычисление индекса соответствия</h4>
                Вычислены индексы соответствия, выбраны топ-3 значения μ: <br>
                <table>
            '''
            for key, value in self.ic.items():
                is_top_3 = value in list(sorted(self.ic.values(), reverse=True))[:3]
                concat += f'''
                    <tr>
                        <td>{key}</td>
                        <td {'style="color: green;"' if is_top_3 else ""}>{value:.5f}</td>
                    </tr>
                '''
            concat += '</table>'
            steps_content += concat
        if self.current_step >= 2:
            steps_content += '''
                <h4>Шаг 3: был загружен частотный словарь</h4>
                источник http://dict.ruslang.ru/freq.php
            '''
        if self.current_step >= 3:
            steps_content += '''
                <h4>Шаг 4: поиск ключей в словаре</h4>
                наиболее вероятные ключи: <br>
                <table>
                <tr>
                    <th>Ключ</th>
                    <th>Подтверждений в тексте</th>
                </tr>
            '''
            for i, kv in enumerate(self.potential_keys):
                key, value = kv
                steps_content += f'''
                    <tr>
                        <td>{key}</td>
                        <td {'style="color: green;"' if i == self.current_selected else ""}>{value}</td>
                    </tr>
                '''
            steps_content += '</table>'
        self.process.setHtml(steps_content)

    def draw_error(self, msg):
        self.process.setHtml(f'<h4 style="color: red">Ошибка:</h4>{msg}')

    def do_step(self):
        self.current_step = (self.current_step + 1) % len(self.step_map)
        if self.current_step == 0:
            self.change_key.setEnabled(False)
            self.open_text.setPlainText('')
            self.current_selected = 0
        try:
            self.step_map[self.current_step]()    
            self.draw_content()
        except Exception as ex:
            self.draw_error(ex)
            print(ex)
            self.current_step = -1
    
    def preprocess_step(self):
        text = self.cipher.toPlainText()
        self.prepocessed, self.lens = preprocess(text)
        if len(text) < 200:
            raise Exception("Слишком короткий текст для расшифровки, необходимая длина от 20μ")
        sub = set(self.prepocessed).difference(set("абвгдежзийклмнопрстуфхцчшщъыьэюя"))
        if len(sub) != 0:
            raise Exception(f"Есть неизвестные символы: {str(sub)}")
    
    def ic_step(self):
        self.ic = get_ic(self.prepocessed, (3, 11))

    def load_frequency_step(self):
        try:
            if self.freq is None:
                self.freq = FrequencyDictionary('êü3/freqrnc2011.csv')
        except:
            raise Exception("Не удалось загрузить частотный словарь")
    
    def search_keys_step(self):
        try:
            best_mu = [x[0] for x in sorted(self.ic.items(), key=lambda x: -x[1])[:3]]
            all_keys_scores = {}
            for mu in best_mu:
                keys_scores = key_search(self.prepocessed, self.freq, mu, 1000)
                all_keys_scores.update(keys_scores)
            self.potential_keys = list(sorted(all_keys_scores.items(), key=lambda x: -x[1])[:10])

            self.open_text.setPlainText(f'Ключ: {self.potential_keys[0][0]}\n'+ \
                    f' Сообщение: {restore_from_split(decode(self.potential_keys[0][0], self.prepocessed), self.lens)}')
            self.change_key.setEnabled(True)
        except:
            raise Exception("Возникла проблема при расшифровке, возможно встречен символ не из алфавита")
        

def main():
    app = QApplication(argv)
    window = App()
    window.show()
    app.exec()  # In PyQt6, exec_() is renamed to exec()

    
if __name__ == '__main__':
    main()