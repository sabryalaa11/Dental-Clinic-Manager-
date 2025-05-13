import sys
from datetime import datetime
import csv
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QSpinBox, QHeaderView, QFileDialog
)
from PyQt6.QtCore import Qt

# القرى
villages = [
    "الحسوة", "المنشية", "المراسفة", "نزلة العرين",
    "البتارخانة", "أبو كبير", "المشاعلة", "أبو سليم",
    "العرب", "أولاد موسى", "منزل ميمون", "الباشا", "السنقبة"
]

# أنواع الحالات
case_types = [
    "حشو", "تقويم", "خلع", "تنظيف", "حشو عصب",
    "تركيب", "تبييض", "كشف", "أشعة", "أخرى"
]

# كلاس الجلسة
class Session:
    def __init__(self, total_sessions):
        self.total_sessions = total_sessions
        self.completed_sessions = 0

    def complete_session(self):
        if self.completed_sessions < self.total_sessions:
            self.completed_sessions += 1
        else:
            pass

# كلاس الحالة
class Case:
    def __init__(self, case_type, price, session=None):
        self.case_type = case_type
        self.price = price
        self.session = session
        self.date = datetime.now()

# كلاس المريض
class Patient:
    def __init__(self, name, age, number, village):
        self.name = name
        self.age = age
        self.number = number
        self.village = village
        self.cases = []

    def add_case(self, case):
        self.cases.append(case)

# نافذة إضافة حالة جديدة
class AddCaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة حالة جديدة")
        self.setLayout(QVBoxLayout())
        self.case_type = QComboBox()
        self.case_type.addItems(case_types)
        self.case_type.setEditable(True)  # يسمح بإضافة أنواع جديدة
        self.price = QLineEdit()
        self.price.setPlaceholderText("بالجنيه المصري")
        self.session_box = QSpinBox()
        self.session_box.setMinimum(0)
        self.session_box.setMaximum(100)
        self.session_box.setValue(0)
        self.session_box.setEnabled(False)
        self.layout().addWidget(QLabel("نوع الحالة:"))
        self.layout().addWidget(self.case_type)
        self.layout().addWidget(QLabel("السعر:"))
        self.layout().addWidget(self.price)
        self.layout().addWidget(QLabel("عدد الجلسات (للحشو/التقويم/حشو عصب):"))
        self.layout().addWidget(self.session_box)
        self.case_type.currentTextChanged.connect(self.toggle_sessions)
        btns = QHBoxLayout()
        self.ok_btn = QPushButton("إضافة")
        self.cancel_btn = QPushButton("إلغاء")
        btns.addWidget(self.ok_btn)
        btns.addWidget(self.cancel_btn)
        self.layout().addLayout(btns)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def toggle_sessions(self):
        t = self.case_type.currentText().strip().lower()
        if t in ["حشو", "تقويم", "حشو عصب", "filling", "braces", "root canal"]:
            self.session_box.setEnabled(True)
        else:
            self.session_box.setEnabled(False)
            self.session_box.setValue(0)

    def get_data(self):
        try:
            price = float(self.price.text())
        except ValueError:
            price = 0
        session = None
        if self.session_box.value() > 0:
            session = Session(self.session_box.value())
        return self.case_type.currentText(), price, session

# النافذة الرئيسية
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("برنامج عيادة الأسنان")
        self.setLayout(QVBoxLayout())
        
        # إضافة حقل البحث
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ادخل اسم المريض للبحث")
        self.search_btn = QPushButton("بحث")
        self.search_btn.clicked.connect(self.search_patient)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        self.layout().addLayout(search_layout)
        
        # قائمة المرضى المسجلين
        patients_layout = QHBoxLayout()
        self.patients_list = QComboBox()
        self.patients_list.setMinimumWidth(200)
        self.load_patients()
        self.patients_list.currentTextChanged.connect(self.patient_selected)
        patients_layout.addWidget(QLabel("المرضى المسجلين:"))
        patients_layout.addWidget(self.patients_list)
        self.layout().addLayout(patients_layout)
        
        # جدول جميع المرضى
        self.all_patients_table = QTableWidget(0, 7)
        self.all_patients_table.setHorizontalHeaderLabels([
            "الاسم", "العمر", "رقم الهاتف", "القرية", "نوع الحالة", "السعر", "التاريخ"
        ])
        self.all_patients_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout().addWidget(QLabel("جميع بيانات المرضى:"))
        self.layout().addWidget(self.all_patients_table)
        
        # زر تحديث الجدول
        self.refresh_all_btn = QPushButton("تحديث بيانات المرضى")
        self.refresh_all_btn.clicked.connect(self.load_all_patients_table)
        self.layout().addWidget(self.refresh_all_btn)
        self.load_all_patients_table()
        
        # بيانات المريض
        form = QHBoxLayout()
        self.name = QLineEdit()
        self.age = QLineEdit()
        self.number = QLineEdit()
        self.village = QComboBox()
        self.village.addItems(villages)
        form.addWidget(QLabel("الاسم:"))
        form.addWidget(self.name)
        form.addWidget(QLabel("العمر:"))
        form.addWidget(self.age)
        form.addWidget(QLabel("رقم الهاتف:"))
        form.addWidget(self.number)
        form.addWidget(QLabel("القرية:"))
        form.addWidget(self.village)
        self.layout().addLayout(form)
        # زر إضافة حالة
        self.add_case_btn = QPushButton("إضافة حالة")
        self.add_case_btn.clicked.connect(self.add_case)
        self.layout().addWidget(self.add_case_btn)
        # جدول الحالات
        self.cases_table = QTableWidget(0, 6)
        self.cases_table.setHorizontalHeaderLabels([
            "نوع الحالة", "السعر", "التاريخ", "عدد الجلسات", "الجلسات المنجزة", "إجراء جلسة"
        ])
        self.cases_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout().addWidget(self.cases_table)
        # أزرار الحفظ والتقرير
        btns = QHBoxLayout()
        self.save_btn = QPushButton("حفظ البيانات")
        self.save_btn.clicked.connect(self.save_data)
        self.report_btn = QPushButton("تقرير المريض")
        self.report_btn.clicked.connect(self.show_report)
        self.view_patient_btn = QPushButton("عرض بيانات المريض")
        self.view_patient_btn.clicked.connect(self.view_patient_data)
        btns.addWidget(self.save_btn)
        btns.addWidget(self.report_btn)
        btns.addWidget(self.view_patient_btn)
        self.layout().addLayout(btns)
        # بيانات البرنامج
        self.patient = None
        self.cases = []
        self.setStyleSheet('''
            QWidget {
                background-color: #23272e;
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit, QComboBox, QSpinBox, QTableWidget, QTableWidgetItem {
                background-color: #2c313c;
                color: #e0e0e0;
                border: 1px solid #444;
            }
            QPushButton {
                background-color: #3b4252;
                color: #e0e0e0;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #4c566a;
            }
            QHeaderView::section {
                background-color: #3b4252;
                color: #e0e0e0;
                border: 1px solid #444;
            }
        ''')

    def add_case(self):
        dialog = AddCaseDialog(self)
        if dialog.exec():
            case_type, price, session = dialog.get_data()
            if not case_type or price <= 0:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال نوع الحالة والسعر بشكل صحيح.")
                return
            case = Case(case_type, price, session)
            self.cases.append(case)
            self.refresh_cases_table()
            # لا تفرغ الحقول هنا بعد إضافة الحالة فقط

    def refresh_cases_table(self):
        self.cases_table.setRowCount(len(self.cases))
        for i, case in enumerate(self.cases):
            self.cases_table.setItem(i, 0, QTableWidgetItem(case.case_type))
            self.cases_table.setItem(i, 1, QTableWidgetItem(str(case.price)))
            self.cases_table.setItem(i, 2, QTableWidgetItem(case.date.strftime('%Y-%m-%d')))
            if case.session:
                self.cases_table.setItem(i, 3, QTableWidgetItem(str(case.session.total_sessions)))
                self.cases_table.setItem(i, 4, QTableWidgetItem(str(case.session.completed_sessions)))
                btn = QPushButton("إكمال جلسة")
                btn.clicked.connect(lambda _, row=i: self.complete_session(row))
                self.cases_table.setCellWidget(i, 5, btn)
            else:
                self.cases_table.setItem(i, 3, QTableWidgetItem("-"))
                self.cases_table.setItem(i, 4, QTableWidgetItem("-"))
                self.cases_table.setCellWidget(i, 5, None)

    def complete_session(self, row):
        case = self.cases[row]
        if case.session:
            if case.session.completed_sessions < case.session.total_sessions:
                case.session.complete_session()
                self.refresh_cases_table()
            else:
                QMessageBox.information(self, "تمت كل الجلسات", "كل الجلسات مكتملة لهذه الحالة.")

    def load_patients(self):
        try:
            with open("clinic_cases.csv", mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                patients = set()
                for row in reader:
                    if row[0].strip():  # إذا كان الاسم غير فارغ
                        patients.add(row[0].strip())
                self.patients_list.clear()
                self.patients_list.addItems(sorted(list(patients)))
        except FileNotFoundError:
            pass

    def patient_selected(self, patient_name):
        if patient_name:
            self.search_input.setText(patient_name)
            self.search_patient()

    def load_all_patients_table(self):
        try:
            with open("clinic_cases.csv", mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
                self.all_patients_table.setRowCount(len(rows))
                for i, row in enumerate(rows):
                    for j in range(7):
                        if j < len(row):
                            self.all_patients_table.setItem(i, j, QTableWidgetItem(row[j]))
                        else:
                            self.all_patients_table.setItem(i, j, QTableWidgetItem(""))
        except FileNotFoundError:
            self.all_patients_table.setRowCount(0)

    def save_data(self):
        name = self.name.text().strip()
        age = self.age.text().strip()
        number = self.number.text().strip()
        village = self.village.currentText()
        if not name or not age or not number:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال جميع بيانات المريض.")
            return
        # الحفظ تلقائي في ملف clinic_cases.csv
        file_path = "clinic_cases.csv"
        patient = Patient(name, age, number, village)
        for case in self.cases:
            patient.add_case(case)
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for case in patient.cases:
                writer.writerow([
                    patient.name,
                    patient.age,
                    patient.number,
                    patient.village,
                    case.case_type,
                    case.price,
                    case.date.strftime('%Y-%m-%d'),
                    case.session.total_sessions if case.session else 0,
                    case.session.completed_sessions if case.session else 0
                ])
        QMessageBox.information(self, "تم الحفظ", "تم حفظ بيانات الحالات بنجاح.")
        self.load_patients()  # تحديث قائمة المرضى بعد الحفظ
        self.load_all_patients_table()  # تحديث جدول جميع المرضى
        # تفريغ الحقول بعد حفظ البيانات
        self.name.clear()
        self.age.clear()
        self.number.clear()
        self.village.setCurrentIndex(0)

    def show_report(self):
        if not self.cases:
            QMessageBox.information(self, "لا توجد حالات", "لم يتم إضافة أي حالات بعد.")
            return
        total_sessions = 0
        total_price = 0
        for c in self.cases:
            if c.session:
                total_sessions += c.session.total_sessions
            total_price += c.price
        msg = f"<b>اسم المريض:</b> {self.name.text()}<br>"
        msg += f"<b>العمر:</b> {self.age.text()}<br>"
        msg += f"<b>رقم الهاتف:</b> {self.number.text()}<br>"
        msg += f"<b>القرية:</b> {self.village.currentText()}<br>"
        msg += f"<hr><b>عدد الحالات:</b> {len(self.cases)}<br>"
        msg += f"<b>إجمالي عدد الجلسات:</b> {total_sessions} جلسة<br>"
        msg += f"<b>إجمالي السعر:</b> {total_price} جنيه<br>"
        QMessageBox.information(self, "تقرير المريض", msg)

    def search_patient(self):
        search_name = self.search_input.text().strip()
        if not search_name:
            QMessageBox.warning(self, "خطأ", "الرجاء إدخال اسم المريض")
            return
        try:
            with open("clinic_cases.csv", mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                found = False
                filtered_rows = []
                for row in reader:
                    if row[0].strip() == search_name:
                        found = True
                        self.name.setText(row[0])
                        self.age.setText(row[1])
                        self.number.setText(row[2])
                        self.village.setCurrentText(row[3])
                        filtered_rows.append(row)
                # عرض بيانات المريض في الجدول الرئيسي
                self.all_patients_table.setRowCount(len(filtered_rows))
                for i, row in enumerate(filtered_rows):
                    for j in range(7):
                        if j < len(row):
                            self.all_patients_table.setItem(i, j, QTableWidgetItem(row[j]))
                        else:
                            self.all_patients_table.setItem(i, j, QTableWidgetItem(""))
                if found:
                    QMessageBox.information(self, "تم العثور على المريض", f"تم العثور على بيانات المريض: {search_name}")
                else:
                    QMessageBox.information(self, "لم يتم العثور", f"لم يتم العثور على مريض باسم: {search_name}")
        except FileNotFoundError:
            QMessageBox.warning(self, "خطأ", "لم يتم العثور على ملف البيانات")

    def view_patient_data(self):
        name = self.name.text().strip()
        if not name:
            QMessageBox.warning(self, "خطأ", "الرجاء إدخال اسم المريض أولاً")
            return
            
        try:
            with open("clinic_cases.csv", mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                patient_cases = []
                for row in reader:
                    if row[0].strip() == name:
                        patient_cases.append(row)
                
                if not patient_cases:
                    QMessageBox.information(self, "لا توجد بيانات", f"لا توجد بيانات للمريض: {name}")
                    return
                
                # عرض البيانات في نافذة منبثقة
                dialog = QDialog(self)
                dialog.setWindowTitle(f"بيانات المريض: {name}")
                dialog.setLayout(QVBoxLayout())
                
                # إنشاء جدول لعرض البيانات
                table = QTableWidget(len(patient_cases), 7)
                table.setHorizontalHeaderLabels([
                    "الاسم", "العمر", "رقم الهاتف", "القرية", 
                    "نوع الحالة", "السعر", "التاريخ"
                ])
                
                for i, case in enumerate(patient_cases):
                    for j, value in enumerate(case[:7]):  # نعرض أول 7 أعمدة فقط
                        table.setItem(i, j, QTableWidgetItem(value))
                
                table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                dialog.layout().addWidget(table)
                
                # زر الإغلاق
                close_btn = QPushButton("إغلاق")
                close_btn.clicked.connect(dialog.close)
                dialog.layout().addWidget(close_btn)
                
                dialog.resize(800, 400)
                dialog.exec()
                
        except FileNotFoundError:
            QMessageBox.warning(self, "خطأ", "لم يتم العثور على ملف البيانات")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(900, 400)
    window.show()
    sys.exit(app.exec()) 