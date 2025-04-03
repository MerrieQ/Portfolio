**The Home Invaders – Smart Home Energy Monitoring Prototype**

File: tEST Copy1223.zip

This project was developed within the context of a data-driven startup concept during a minor. The objective was to design a smart home system aimed at monitoring energy consumption, minimizing unnecessary electricity usage, safeguarding user privacy, and simplifying the process of integrating new smart devices into the system. The presented prototype focuses specifically on the connection process of a smart outlet. Initially, the use of an NFC chip was considered; however, due to resource limitations, a proximity sensor was implemented as a practical alternative.

The prototype was created using Arduino (C/C++) and simulated in Wokwi. No Python was used in this project.

**Getting Started**
To test the prototype, you’ll need an Arduino simulation environment (e.g. Wokwi) or a physical Arduino board (e.g. Uno or Nano).

**Prerequisites**
- Arduino IDE or Wokwi.com (browser-based)
- Required components (see diagram.json):
  - Current sensor
  - LEDs
  - Display module (if applicable)
  

**Installation**
1. Open the file sketch.ino in your Arduino IDE or upload it to Wokwi.
2. Refer to diagram.json to understand the breadboard wiring and component setup.
3. Verify and upload the sketch to the Arduino board, or simulate using Wokwi.
4. Install libraries listed in libraries.txt.

**Usage**
This prototype shows how a smart outlet could be added to a smart home system in a simple and user-friendly way. When the system detects someone nearby—using a proximity sensor—it gives visual feedback with a LED-Display. This simulates the connection process of a new smart device. While this version does not measure real energy usage, it demonstrates how future smart devices could be connected easily, with clear feedback and a focus on privacy and ease of use.

**Project Context**
This code was part of a group project under the name “The Home Invaders.” It accompanied a broader smart-home system concept focused on:
- Real-time energy tracking
- Recommendations for energy saving
- Privacy-first data handling


**License**
No license attached. You are free to use, adapt, or repurpose this code.

**Contact**
Merlijn Marquering  
Email: merlijn.marquering@gmail.com
GitHub: https://github.com/MerrieQ  

**Acknowledgments**
- Wokwi.com – for fast Arduino simulation
- Arduino – microcontroller ecosystem

