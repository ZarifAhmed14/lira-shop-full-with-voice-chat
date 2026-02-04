# Voice AI Chatbot Implementation Walkthrough

I have successfully upgraded the Lira Cosmetics Chatbot with Voice AI capabilities.

## Features Implemented

1.  **Voice Input (Speech-to-Text)**
    *   Added `VoiceRecorder` component in the frontend.
    *   Integrated **Groq Whisper API** in the backend (`stt_handler.py`).
    *   Users can record audio which is transcribed and sent to the chatbot.

2.  **Voice Output (Text-to-Speech)**
    *   Added `AudioPlayer` component in the frontend.
    *   Integrated **Edge TTS** (Free) in the backend (`tts_handler.py`).
    *   AI responses are automatically converted to speech if Voice Mode is active.

3.  **UI Enhancements**
    *   **Voice Mode Toggle**: Switch between Text and Voice modes.
    *   **Recording Indicator**: Visual feedback during recording.
    *   **Audio Controls**: Play/Pause/Volume for AI responses.

4.  **Cost Tracking Integration**
    *   Updated `CostCalculator` to track STT (per minute) and TTS (per char) costs.
    *   Simulation script updated to include voice query costs.

## Files Created/Modified

### Backend (`project/`)
*   `stt_handler.py`: Handles audio transcription.
*   `tts_handler.py`: Handles speech synthesis.
*   `cost_calculator.py`: Updated with voice pricing logic.
*   `app.py`: Added `/api/voice/*` endpoints.
*   `simulation.py`: Simulation 50% voice traffic.
*   `report_generator.py`: Generates PDF with voice cost analysis.

### Frontend (`frontend/src/`)
*   `components/chat/VoiceRecorder.tsx`: New recording component.
*   `components/chat/AudioPlayer.tsx`: New audio player component.
*   `pages/Chat.tsx`: Integrated voice components and logic.

## How to Run

1.  **Backend Terminal**:
    First, install the new voice dependencies, then start the Flask server.
    ```powershell
    cd d:\lira-shop-full\lira-shop-full-main\project
    pip install -r requirements.txt
    python app.py
    ```

2.  **Frontend Terminal**:
    Start the React development server.
    ```powershell
    cd d:\lira-shop-full\lira-shop-full-main\frontend
    npm run dev
    ```

3.  **Report Generation**:
    ```powershell
    cd d:\lira-shop-full\lira-shop-full-main\project
    python simulation.py
    python report_generator.py
    ```
    The report will be saved as `voice_report_<timestamp>.pdf`.

## Verification Results
*   **Simulation**: Ran 50 queries (mixed text/voice).
*   **Report**: Generated `voice_report_1769699707.pdf`.
