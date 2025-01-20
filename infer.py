import os
import cv2
import torch
from ultralytics import YOLO
import shutil

# 定义类别名称列表
class_names = [
    "Atrophaneura_varuna", "Byasa_alcinous", "Graphium_agamemnon", "Graphium_cloanthus",
    "Graphium_sarpedon", "Iphiclides_podalirius", "Lamproptera_curius", "Lamproptera_meges",
    "Meandrusa_payeni", "Meandrusa_sciron", "Pachliopta_aristolochiae", "Pathysa_antiphates",
    "Pazala_eurous", "Teinopalpus_aureus", "Teinopalpus_imperialis", "Troides_helena",
    "Troides_aeacus", "Bhutanitis_lidderdalii", "Sericinus_montelus", "Parnassius_apollo",
    "Parnassius_nomion", "Parnassius_phoebus", "Catopsilia_pomona", "Catopsilia_pyranthe",
    "Catopsilia_scylla", "Colias_erate", "Colias_fieldii", "Eurema_blanda", "Eurema_andersoni",
    "Eurema_brigitta", "Eurema_hecabe", "Eurema_laeta", "Gonepteryx_rhamni", "Apatura_iris",
    "Chitoria_ulupi", "Hestina_assimilis", "Rohana_parisatis", "Ariadne_ariadne", "Euthalia_niepelti",
    "Athyma_perius", "Limenitis_sulpitia", "Neptis_hylas", "Cyrestis_thyodamas", "Stibochiona_nicea",
    "Allotinus_drumila", "Miletus_chinensis", "Taraka_hamada", "Curetis_acuta", "Arhopala_paramuta",
    "Arhopala_rama", "Artipe_eryx", "Horaga_albimacula", "Horaga_onyx", "Ampittia_virgata",
    "Ancistroides_nigrita", "Astictopterus_jama", "Erionota_torus", "Iambrix_salsala",
    "Isoteinon_lamprospilus", "Parnara_guttata", "Notocrypta_curvifascia", "Udaspes_folus",
    "Seseria_dohertyi"
]

# 加载YOLOv8模型
def load_model(model_path):
    model = YOLO(model_path)
    return model

# 使用YOLOv8模型进行图像识别并绘制检测框
def predict_and_draw_boxes(image_path, model, output_folder, ok_folder):
    # 从文件名中提取真实类别
    filename = os.path.basename(image_path)
    true_class = filename.split(" ")[0]  # 提取类别名称
    
    # 使用YOLOv8模型进行预测
    results = model(image_path, iou=0.6)
    # 读取图像
    image = cv2.imread(image_path)
    
    is_correct = False
    max_conf = 0.0
    
    # 检查是否有检测结果
    if len(results) > 0 and len(results[0].boxes) > 0:
        for result in results:
            for box in result.boxes:
                # 获取每个检测框的信息
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # 边界框坐标
                conf = float(box.conf[0])  # 置信度
                cls = int(box.cls[0])  # 类别

                # 获取类别名称
                class_name = class_names[cls]
                
                # 检查是否正确识别且置信度大于0.8
                if class_name == true_class and conf > 0.8:
                    is_correct = True
                    max_conf = max(max_conf, conf)

                # 绘制边界框
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # 在框上方绘制标签
                label = f"{class_name}: {conf:.2f}"
                cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 如果没有检测到任何目标，添加提示文字
    else:
        cv2.putText(image, "No detection", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # 保存带有检测框的图像
    output_image_path = os.path.join(output_folder, filename)
    cv2.imwrite(output_image_path, image)
    
    # 如果正确识别且置信度大于0.8，将原图复制到ok文件夹
    if is_correct:
        ok_image_path = os.path.join(ok_folder, filename)
        # 检查源文件和目标文件是否相同
        if os.path.abspath(image_path) != os.path.abspath(ok_image_path):
            shutil.copy2(image_path, ok_image_path)
    
    return is_correct, max_conf

def process_images(input_folder, output_folder, ok_folder):
    # 确保结果文件夹和ok文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(ok_folder):
        os.makedirs(ok_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_path = os.path.join(input_folder, filename)
            predict_and_draw_boxes(image_path, model, output_folder, ok_folder)

if __name__ == "__main__":
    input_folder = "photo"  # 图片所在文件夹
    output_folder = "result"  # 保存标注结果的文件夹
    ok_folder = "ok"  # 正确识别图片的文件夹
    model_path = "best-4.pt"  # 替换为你的模型文件名
    model = load_model(model_path)
    process_images(input_folder, output_folder, ok_folder)
