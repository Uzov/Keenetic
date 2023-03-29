Установил на Entware клиента Radius для аутентификации через пользователей по SSH, в целом работает! Для этого использовал подключаемый модуль PAM (Pluggable Authentication Module).
Исходники модуля скачал отсюда https://freeradius.org/sub_projects/, а затем скомпилировал в Entware (по инструкции). Получил модуль pam_radius_auth.so.
Установил пакет openssh-server-pam - 9.0p1-1 - OpenSSH server (with PAM support). Установил FreeRadius.
Настроил в /opt/etc/pam.d/sshd (фрагмент):
# Standard Un*x authentication.
# auth       include      common-auth
auth       required       /opt/lib/security/pam_radius_auth.so debug conf=/opt/etc/pam_radius_auth.conf try_first_pass client_id=Keenetic

Настроил (по инструкции):
/opt/etc/ssh/sshd_config
/opt/etc/pam_radius_auth.conf

Для архивации прошивки нужно использовать tar в варианте gnu (не posix). Пример, можно в консоли через программу tar упаковать содержимое директории t:
tar czvf a.tar.gz -C t .

Папка packages содержит не все пакеты! При установке прошивки возможно появится необходимость дополнить папку packages другими пакетами Entware. 

Выявленные проблемы:
1.	Radius сервер выдаёт ошибку авторизации, т.к. клиент передаёт не тот пароль (всегда один и тот же) User-Password = "\010\n\r\177INCORR".
Известная причина: на Keenetic необходимо завести локального пользователя с тем же именем, пароль м.б. любой, home директорий не обязательно. Тогда Radius клиент сможет передать серверу UID пользователя, и сервер отвечает Access-Accept, т.е. всё нормально. (https://freeradius-users.freeradius.narkive.com/ass1x6nY/libpam-radius-auth-password-problem)
Возможное решение проблемы: локальных пользователей на Keenetic заводить скриптом, т.е. брать их с центрального сервера (того же Radius или LDAP+Radius). Потом заводить/удалять локальных пользователей на всех Кинетиках. По идее такому пользователю не нужен ни локальный пароль, ни папка home. Не получилось аутентифицировать через Radius пользователя с пустым локальным паролем, возможно что-то недонастроил в ssh_config.
Идею про скрипт взял отсюда: https://www.linuxquestions.org/questions/programming-9/openssh-and-pam-900406/
2.	Модуль pam_radius_auth.so использует аутентификацию типа PAP, т.е. пароль передаётся по сети в MD5. 