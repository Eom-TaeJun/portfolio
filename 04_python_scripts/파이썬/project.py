import sys
import copy
import os

D=[]

def get_grade(avg):
    if avg >= 90:
        return "A"
    elif avg >= 80:
        return "B"
    elif avg >= 70:
        return "C"
    elif avg >= 60:
        return "D"
    else:
        return "F"

def show(filename="students.txt", reload=False):
    global D

    if reload or not D:  # ✅ 처음 실행하거나 D가 비어있을 경우 파일에서 로드
        D = []  
        filename = os.path.abspath(filename)  

        if not os.path.exists(filename):
            print(f"❌ Error: File '{filename}' not found.")
            return

        print(f"✅ Using file: {filename}")

        with open(filename, "r") as file:
            for line in file:
                student_data = line.strip().split("\t")
                if len(student_data) != 4:
                    print(f"⚠️ Skipping invalid line: {line.strip()}")
                    continue  

                student, s_name, s_mid, s_fin = student_data
                mid, fin = int(s_mid), int(s_fin)
                avg = round((mid + fin) / 2, 1)
                grade = get_grade(avg)

                D.append([student, s_name, s_mid, s_fin, str(avg), grade])  

        if not D:
            print("⚠️ No valid student data found in file.")
            return

        D.sort(key=lambda x: float(x[4]), reverse=True)  

    # ✅ 정렬된 테이블 출력 (학번 8자리, 이름 15자리, Mid/Final 3자리, 평균 4자리, 학점 1자리)
    print("\n{:<8} {:<15} {:>3} {:>3} {:>4} {:>1}".format("Student", "Name", "Mid", "Fin", "Avg", "G"))
    print("-" * 40)

    for r in D:
        print("{:<8} {:<15} {:>3} {:>3} {:>4} {:>1}".format(
            r[0], 
            r[1].ljust(15),  # 이름이 15자리보다 짧으면 공백 추가
            r[2], 
            r[3], 
            "{:.1f}".format(float(r[4])),  # 평균은 소수점 1자리까지 표시
            r[5]
        ))





def search():
    s_id = input("ID: ")
    for student in D:
        if student[0] == s_id:
            print("\t".join(student))
            return
    print("NO SUCH PERSON")

def changescore():
    global D
    s_id = input("Student ID: ")

    for i in range(len(D)):
        if D[i][0] == s_id:
            cho = input("\nMid/Final? ").lower()
            if cho not in ["mid", "final"]:
                return

            n_score = input("Input new score: ")
            if not n_score.isdigit() or not (0 <= int(n_score) <= 100):
                return

            print("\n{:<8} {:<15} {:>3} {:>3} {:>4} {:>1}".format("Student", "Name", "Mid", "Fin", "Avg", "G"))
            print("-" * 40)
            print("\t".join(D[i]))

            if cho == "mid":
                D[i][2] = n_score
            else:
                D[i][3] = n_score

            avg = round((int(D[i][2]) + int(D[i][3])) / 2, 1)
            grade = get_grade(avg)

            D[i][4] = str(avg)  
            D[i][5] = grade  

            print("Score changed")
            print("\t".join(D[i]))
            return

    print("NO SUCH PERSON.")


                   
def add():
    global D
    s_id = input("Student ID: ")

    for student in D:
        if student[0] == s_id:
            print("ALREADY EXISTS.")
            return

    s_name = input("Name: ")
    s_mid = input("Midterm Score: ")
    s_fin = input("Final Score: ")

    if not s_mid.isdigit() or not s_fin.isdigit():
        print("Invalid input.")
        return

    avg = round((int(s_mid) + int(s_fin)) / 2, 1)
    grade = get_grade(avg)

    D.append([s_id, s_name, s_mid, s_fin, str(avg), grade])  
    print("Student added.")

     
def searchgrade():
    s_grade = input("Grade to search: ").upper()

    if s_grade not in ["A", "B", "C", "D", "F"]:
        return

    found = False
    for student in D:
        if student[5] == s_grade:
            print("\t".join(student))
            found = True

    if not found:
        print("NO RESULTS")

def remove():
    global D
    if not D:
        print("List is empty")
        return

    s_id = input("ID: ")
   
    for i in range(len(D)):
        if D[i][0] == s_id:
            print("Student removed.")
            del D[i]
            return

    print("NO SUCH PERSON.")  
def quit():
    global D
    save = input("Save data? [yes/no] ").strip().lower()

    if save == "yes":
        f_name = input("File name: ").strip()

        sorted_D = sorted(D, key=lambda x: float(x[4]), reverse=True)

        with open(f_name, "w") as file:
            for student in sorted_D:
                file.write("\t".join(student[:4]) + "\n")


    print("$")
    sys.exit()


def main():
    global D
    print("🚀 main() 실행됨")

    filename = input("Enter file name (default: students.txt): ").strip()
    if not filename:
        filename = "students.txt" 

    show(filename, reload=True)  

    while True:
        command = input("# ").strip().lower()  
        if command == "show":
            show()
        elif command == "search":
            search()
        elif command == "changescore":
            changescore()
        elif command == "add":
            add()
        elif command == "searchgrade":
            searchgrade()
        elif command == "remove":
            remove()
        elif command == "quit":
            quit()




if __name__ == "__main__":
    main()
           


