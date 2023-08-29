# Cloud Platform User Manual

1. Go to the website: https://clpl.speit.site/ and enter the account and password to log in.
    ![](./img/user_manual_1.png)
2. Then click“+” to create a pod.
    ![](./img/user_manual_2.png)
3. The interface “Create Pod” is displayed, fill in the required fields (default values or set by yourself) and then click the Save button.

   > Attention: All required fields need to be filled in, otherwise the save operation will fail.

   - Name: Enter the name of the pod.
   - Description: Some description of the pod.
   - Template:
     - Template-default: Default template;
     - Template-math: Templates that contain java tool;
     - Template-ie: Templates that contain wxmaxima tool;
   - Timeout: The amount of time the program can continue to run after the user closes the page or disconnects;
   - CPU Limit: CPU performance limitations;
   - Memory Limit: The memory space required by the program;
   - Storage Limit: The storage space required by the program, more than 10G;
   ![](./img/user_manual_3.png)

4. After the Pod is created, you can edit, delete, stop, and connect to it.
    ![](./img/user_manual_4.png)
5. By clicking CONNECT, you can choose to connect to WEBIDE or VNC.
    ![](./img/user_manual_5.png)
6. Click WEBIDE to jump to a new page, and then input the account and password to enter the code editing page.
    
    ![](./img/user_manual_6_1.png)
    > Attention: If the 503 page appears, it is because the server needs to wait a minute to prepare the resource.

    ![](./img/user_manual_6_2.png)
    > Attention: After entering WEBIDE, make sure to save the file in the root directory, otherwise it will be deleted after the program ends.
    
7. Click VNC to jump to a new page, and then input the account and password to enter the virtual desktop.
    ![](./img/user_manual_7_1.png)
    ![](./img/user_manual_7_2.png)