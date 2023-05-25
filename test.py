import serial  # 시리얼 통신을 위한 모듈
import threading  # 스레드를 위한 모듈
import time  # 시간 관련 모듈

DEV_PLATFORM = 'DESKTOP'
    
if DEV_PLATFORM == 'DESKTOP':
    port = 'COM5'
else:
    port = '/dev/ttyS0'
baud = 115200  # serial speed, 통신 속도

ser = serial.Serial(  # 시리얼 포트 설정
   port = port,
   baudrate = baud,
   bytesize = serial.EIGHTBITS,
   parity = serial.PARITY_NONE,
   stopbits = serial.STOPBITS_ONE,
   timeout = 5
)
line = ''  # 수신한 데이터 저장
alive = True  # 스레드 실행 여부
endcommand = False  # 종료 명령 여부   

# 쓰레드
def readthread(ser):  # 데이터 읽어오는 역할, 별도의 스레드로 실행
    global line
    global endcommand
    
    print('readthread init')

    while alive:  # 쓰레드 실행되면 루프
        try:
            for c in ser.read():  # 1바이트씩 데이터 읽어옴
                line += (chr(c))  # 데이터를 문자열로 추가
                if line.startswith('['):  # []로 문자열이 되면, 출력하고 종료 명령인지 확인
                    if line.endswith(']'):
                        print('receive data=' + line)
                        if line == '[end]':
                            endcommand = True
                            print('end command\n')
                        # line reset
                        line = ''
                        ser.write('ok'.encode())  # 수신 완료 메시지를 시리얼 포트로 전송
                else:  # 그렇지 않으면 초기화
                    line = ''
        except Exception as e:  # 예외 발생
            print('read exception')
            
    print('thread exit')  # 쓰레드 종료시 출력
    
    ser.close()  # 시리얼 포트 닫음
    
def main():
    global endcommand
    
    # 시리얼 쓰레드 생성
    thread = threading.Thread(target=readthread, args=(ser,))  # ser인자 전달, 함수를 쓰레드로 실행
    thread.daemon = True
    thread.start()

    if DEV_PLATFORM == 'DESKTOP':  # 시리얼 통신을 테스트하기 위해, 0-9 숫자를 포함한 메시지 전송
        for count in range(0, 10):
            strcmd = '[test' + str(count) + ']'
            print('send data=' + strcmd)
            strencoding = strcmd.encode()  # 문자열 인코딩
            ser.write(strencoding)  # 시리얼 포트로 전송
            time.sleep(1)  # 1초 대기
            
        strcmd = '[end]'  # [end]메시지를 전송하여 종료 명령 보냄
        ser.write(strcmd.encode())
        print('send data=' + strcmd)
        
    else:
        while True:
            time.sleep(1)
            if endcommand is True:
                break

    print('main exit')
    alive = False
    exit()
    
main()
