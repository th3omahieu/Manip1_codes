def flir_video(vid, tempsexp, DXmax, DYmax, Xinmax, Yinmax, valeur_max):
    # 1. Initialization
    tempsexp_ms = int(tempsexp * 1000)
    valeur_min = 11
    valeur_max_ms = int(valeur_max * 1000)
    
    # Define ROI (Note: Python/OpenCV usually handles ROI via array slicing)
    # roi = [Xinmax, Yinmax, DXmax, DYmax]
    
    # 2. Setup Figure/Window
    window_name = "FLIR Video Stream"
    cv2.namedWindow(window_name)

    # 3. Create Slider (Trackbar)
    def on_change(val):
        nonlocal tempsexp_ms
        # Ensure it doesn't go below the camera minimum
        tempsexp_ms = max(val, valeur_min)
        # Update camera hardware attribute
        # Assuming your python camera object 'vid' has a similar setter
        vid.set_exposure_time(tempsexp_ms)

    cv2.createTrackbar("Exposure (ms)", window_name, tempsexp_ms, valeur_max_ms, on_change)

    # 4. Start Acquisition
    vid.start()
    print("Streaming... Press 'q' or close window to stop.")
    
    try:
        # 5. Main Loop 
        while True:
            # Capture frame
            ret, frame = vid.get_snapshot()
            
            if not ret:
                break

            # Apply ROI if needed (y:y+h, x:x+w)
            roi_frame = frame[Yinmax:Yinmax+DYmax, Xinmax:Xinmax+DXmax]

            # Display (equivalent to imagesc)
            display_frame = cv2.applyColorMap(roi_frame, cv2.COLORMAP_JET)
            cv2.imshow(window_name, display_frame)

            # 6. Handle Events (Pause/Update/Break)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            # Check if window was closed via the [X] button
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

    finally:
        # 7. Cleanup
        vid.stop()
        cv2.destroyAllWindows()
        
    # Return back in seconds
    return tempsexp_ms / 1000.0

