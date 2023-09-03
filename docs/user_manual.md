# Cloud Platform User Manual

## Login

Navigate to your deployment website: https://host.example.com/ and enter the account and password to log in. If OIDC login is configured, click the OIDC button.

![1](./img/user_manual_1.png)

## Pod Management

Here is a short explanation of functions

![2](./img/user_manual_2.png)

1. Add Pod
2. Click to log out
3. Navigate to Profile Management
4. Contact admin by email

### Pod Creation

When the add pod button is clicked, the interface “Create Pod” will be displayed, fill in the required fields (default values or set by users) and then click the Save button.

![3](./img/user_manual_3.png)

   - **Name**: Enter the name of the pod.
   - **Description**: Some description of the pod.
   - **Template**: usually the default template would do just fine.
   - **Timeout**: The amount of time the program can continue to run after the user closes the page or disconnects;
   - **CPU Limit**: CPU performance limitations 1000 = 1CPU core
   - **Memory Limit**: The memory space required by the program, in MB;
   - **Storage Limit**: The storage space required by the program, must be greater than 10G;

   > Attention: All required fields need to be filled in, otherwise the save operation will fail.

After creation, refreshes are requried to load the new pod information
![4](./img/user_manual_4.png)

In case the pod's **CONNECT** button stuck in disabled for long time, click the **EDIT** button and set its status to "running" to force start it
![5](./img/user_manual_5.png)
![6](./img/user_manual_6.png)

### Pod Power

Click the **START**/**STOP** button to turn the Pod ON/OFF.

### Pod Connection

By clicking **CONNECT**, users can choose to connect to WEBIDE or VNC in the drop-down menu. Users will be redirected to new page, the page is automatically authenticated.

![7](./img/user_manual_7.png)

> WebIDE
>
> ![8](./img/user_manual_8.png)

> VNC Virtual Desktop
>
> ![9](./img/user_manual_9.png)

> Attention: If the 503 page appears, it is because the server needs to wait a minute to prepare the resource.
>
> ![10](./img/user_manual_10.png)

> Attention: Make sure to save the file in the `/root` directory, otherwise it will be deleted after the pod shutdown. Storing files on the Desktop is fine.

### Pod Removal

Click the **DELETE** button to delete a pod. **All data stored in pod will be deleted.**

![11](./img/user_manual_11.png)

## Profile Management

Click the Profile button and navigate to profile management page.

![12](./img/user_manual_12.png)

User can check their quota, modify their email and password.

![13](./img/user_manual_13.png)

> Attention: OIDC users cannot change their password

> Attention: The email users configure will associate their avatars with [Gravatar](http://cn.gravatar.com/): they will be displayed along their usernames.
