
        cv2.line(img, (x, 0), (x, height), (0, 0, 0), 2)   

    for y in range(0, height, 100):
        cv2.line(img, (0, y), (width, y), (0,0,0), 2) 