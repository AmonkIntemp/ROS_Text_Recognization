import rclpy
from rclpy.node import Node
from example_interfaces.msg import String
from paddleocr import PaddleOCR, draw_ocr
import cv2
import time
import inspect


def debug_print(*args, **kwargs):
    # 获取当前调用信息
    frame = inspect.currentframe().f_back
    file_name = frame.f_code.co_filename
    line_no = frame.f_lineno
    func_name = frame.f_code.co_name

    # 格式化输出调试信息
    print(f"[{file_name}:{line_no} in {func_name}]", *args, **kwargs)

class StringPublisher(Node):
    def __init__(self):
        super().__init__('string_publisher')
        self.publisher_ = self.create_publisher(String, 'string_topic', 10)  # 发布到 'string_topic'
        #self.timer = self.create_timer(1.0, self.publish_string_message)
        #self.videoFrame_recognition()


    def publish_string_message(self):
        msg = String()
        msg.data = 'Hello, ROS 2 from Python!'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published: {msg.data}')

    def single_area_matching(self,area,valid_area):
        x_min, y_min, x_max, y_max = valid_area
        for point in area:
            if x_min>point[0] or point[0]>x_max or y_min>point[1] or point[1]>y_max:
                return False
        return True

    def is_in_validArea(self,box,txts,scores,G_valid_area,CPS_valid_area):
        print("33")
        ret_box=[]
        ret_txts=[]
        ret_scores=[]
        print("36")
        for area,txt,score in zip(box,txts,scores):
            if self.single_area_matching(area,G_valid_area):
                ret_box.append(area)
                ret_txts.append(txt)
                ret_scores.append(score)
            elif self.single_area_matching(area,CPS_valid_area):
                ret_box.append(area)
                ret_txts.append(txt)
                ret_scores.append(score)
            else:
                continue
        return ret_box,ret_txts,ret_scores

    def videoFrame_recognition(self):
        ocr = PaddleOCR(lang="en")
        cap = cv2.VideoCapture(4)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 5)

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # 打印相机的分辨率和帧率
        print(f"Frame Width: {frame_width}")
        print(f"Frame Height: {frame_height}")
        print(f"FPS: {fps}")
        G_valid_area=[450,295,525,345]
        CPS_valid_area=[545,295,610,345]
        print("67")
        while cap.isOpened():
            ret,frame = cap.read()
            if not ret:
                break
            debug_print("debug_message")
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = ocr.ocr(rgb_frame,cls=False)       #RGB的图片格式？这个第一个输入居然是numpy数组？
            debug_print("debug_message")
            if result and result[0] != None:
                debug_print("debug_message")
                boxes = [line[0] for line in result[0]]
                txts = [line[1][0] for line in result[0]]
                scores = [line[1][1] for line in result[0]]
                debug_print("debug_message")
                boxes,txts,scores=self.is_in_validArea(boxes,txts,scores,G_valid_area,CPS_valid_area)
                debug_print("debug_message")
                #for line in result[0]返回的line为result[0]的每一行,line[0]就是该行的第一行元素
                if not boxes:
                    continue
                debug_print("debug_message")
                msg=String()
                msg.data="uSV/h: "+str(txts[0])+"cps: "+str(txts[1])
                self.publisher_.publish(msg)
                self.get_logger().info(msg.data)
                im_show = draw_ocr(rgb_frame,boxes,txts,scores,font_path='/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc')
                frame = cv2.cvtColor(im_show,cv2.COLOR_RGB2BGR)
            else:
                time.sleep(0.05)       #延迟真凶？
            cv2.imshow('PaddleOCR Realtime', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

def main(args=None):
    rclpy.init(args=args)
    node = StringPublisher()
    node.videoFrame_recognition()
    rclpy.spin(node)
    rclpy.shutdown()

