#!/bin/bash

HOST=�Ώۃz�X�g��(IP�A�h���X)
USER=twsys10
PASS=twsys10
TARGET_DIR=�o�b�N�A�b�v�f�B���N�g��(�t�@�C��)
BACKUP_DIR=�ۑ���f�B���N�g��

expect -c "
set timeout -1
spawn scp -Cpr ${TARGET_DIR} ${USER}@${HOST}:${BACKUP_DIR}
expect {
  \" Are you sure you want to continue connecting (yes/no)? \" {
    send \"yse\r\"
    expect \"password:\"
    send \"${PASS}\r\"
  } \"password:\" {
    send \"${PASS}\r\"
  }
}
interact
"