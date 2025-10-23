[app]
title = Kabab Inventory
package.name = kababinventory
package.domain = com.yourname.kababinventory

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 0.1
requirements = python3,kivy==2.3.1,sqlite3,openssl

orientation = portrait
fullscreen = 0

# تنظیمات اندروید
android.api = 33
android.minapi = 21
android.sdk = 23
android.ndk = 25b
android.gradle_dependencies = 'com.android.tools.build:gradle:7.1.2'

# مجوزها
android.permissions = INTERNET

# معماری
android.arch = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
