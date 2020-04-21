import h5py as h5
import os
import numpy as np
import cv2


def ExtractDataFrom_hdf(data_name):
    #  ich habe einene folder mit der name hdfFiles wo ich die hdf daten schpeichere.
    #  der E_von vorne ohne Schulterstütze muss den gleichne name wie der hdf folder sein

    folder_name = os.path.join("hdfFiles", data_name)  # hdf folder path
    saveToPath = os.path.join("extractedData", data_name)  # video save to path
    print(folder_name)
    #  anzahl der daten in hdfFiles
    path, dirs, files = next(os.walk(folder_name))
    file_count = len(files)

    depth_array = []
    ir_array = []
    registered_array = []

    blank_image = np.zeros((512, 424, 3), np.uint8)  # blank image if the frame don't exists

    for i in range(0, file_count):
        file_name = os.path.join(folder_name, "1_" + str(i) + ".hdf")
        print(file_name)
        # %% open the hdf file and its sup_parts
        try:  # some hdf files don't open
            f = h5.File(file_name, "r")
            # %% initial the sup_parts
            try:  # depth and ir data have to be int and 0->255
                MetaData = f['LabelData']['MetaData']
                color = f['SensorData']['color']
                depth = f['SensorData']['depth']
                ir = f['SensorData']['ir']
                registered = f['SensorData']['registered']

                # get image size
                height, width, layers = registered.shape
                size = (width, height)

                # convert the data to array so later convert them cv2 format
                ir_np = np.asarray(ir)
                depth_np = np.asarray(depth)
                array_registered = np.asarray(registered)

                # convert data to cv2 format
                cv2_registered = cv2.cvtColor(array_registered, cv2.COLOR_BGR2RGB)

                # append data to te list
                ir_array.append(ir_np)
                depth_array.append(depth_np)
                registered_array.append(cv2_registered)
            except:  # if the image don't exists put a blankImage to have the wright number of frames
                print("jumped frame", i)
                registered_array.append(blank_image)
        except:
            print("file cant be opened", file_name)
            registered_array.append(blank_image)

    #  make sure that the path exist
    if not os.path.exists("extractedData"):
        os.mkdir("extractedData")
    if not os.path.exists(saveToPath):
        os.mkdir(saveToPath)

    save_To_ir_path = os.path.join(saveToPath, data_name+'ir.npy')
    save_To_depth_path = os.path.join(saveToPath, data_name+'depth.npy')
    save_To_color_path = os.path.join(saveToPath, data_name+'color.avi')

    np.save(save_To_ir_path, ir_array)
    np.save(save_To_depth_path, depth_array)
    out_registered = cv2.VideoWriter(save_To_color_path, cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
    for i in range(len(registered_array)):
        image = cv2.cvtColor(registered_array[i], cv2.COLOR_BGR2RGB)
        out_registered.write(image)

    out_registered.release()


if __name__ == "__main__":
    data_name = "E_von vorne ohne Schulterstütze"
    ExtractDataFrom_hdf(data_name)
