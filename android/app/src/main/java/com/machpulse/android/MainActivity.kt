package com.machpulse.android

import android.app.Activity
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import org.json.JSONArray
import org.json.JSONObject
import kotlin.math.max


class MainActivity :
    Activity(),
    SensorEventListener {

    companion object {

        private const val MACHINE_ID = "M01"

        /*
         * IMPORTANT:
         * Replace YOUR_MAC_IP with the IP address
         * returned by:
         *
         * ipconfig getifaddr en0
         *
         * Example:
         * ws://192.168.1.10:8000/ws/monitor/M01
         */
        private const val SERVER_URL =
            "ws://192.168.1.4:8000/ws/monitor/M01"

        private const val WINDOW_SIZE = 256
    }


    private lateinit var sensorManager: SensorManager

    private var accelerometer: Sensor? = null


    private lateinit var statusText: TextView
    private lateinit var sampleText: TextView
    private lateinit var rateText: TextView
    private lateinit var sensorText: TextView


    private val httpClient =
        OkHttpClient()


    private var webSocket: WebSocket? = null

    private var monitoring = false


    private val xSamples =
        mutableListOf<Float>()

    private val ySamples =
        mutableListOf<Float>()

    private val zSamples =
        mutableListOf<Float>()


    private var firstSensorTimestampNs =
        0L

    private var lastSensorTimestampNs =
        0L


    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(savedInstanceState)

        setContentView(
            R.layout.activity_main
        )


        statusText =
            findViewById(R.id.statusText)

        sampleText =
            findViewById(R.id.sampleText)

        rateText =
            findViewById(R.id.rateText)

        sensorText =
            findViewById(R.id.sensorText)


        sensorManager =
            getSystemService(
                SENSOR_SERVICE
            ) as SensorManager


        accelerometer =
            sensorManager.getDefaultSensor(
                Sensor.TYPE_ACCELEROMETER
            )


        if (accelerometer == null) {

            sensorText.text =
                "Accelerometer: NOT AVAILABLE"

        } else {

            sensorText.text =
                "Accelerometer: available"
        }


        findViewById<Button>(
            R.id.startButton
        ).setOnClickListener {

            startMonitoring()
        }


        findViewById<Button>(
            R.id.stopButton
        ).setOnClickListener {

            stopMonitoring()
        }
    }


    private fun startMonitoring() {

        if (monitoring) {
            return
        }


        val sensor =
            accelerometer

        if (sensor == null) {

            statusText.text =
                "Accelerometer unavailable"

            return
        }


        clearSamples()

        connectWebSocket()


        monitoring = true


        /*
         * SENSOR_DELAY_GAME is a suggested delay,
         * not a guaranteed sampling rate.
         *
         * We calculate the real rate from
         * SensorEvent timestamps.
         */
        sensorManager.registerListener(
            this,
            sensor,
            SensorManager.SENSOR_DELAY_GAME
        )


        statusText.text =
            "Starting monitoring..."
    }


    private fun stopMonitoring() {

        monitoring = false


        sensorManager.unregisterListener(
            this
        )


        webSocket?.close(
            1000,
            "Monitoring stopped"
        )

        webSocket = null


        clearSamples()


        statusText.text =
            "Stopped"

        sampleText.text =
            "Samples: 0 / $WINDOW_SIZE"

        rateText.text =
            "Sample rate: -- Hz"
    }


    private fun connectWebSocket() {

        val request =
            Request.Builder()
                .url(SERVER_URL)
                .build()


        webSocket =
            httpClient.newWebSocket(
                request,
                object : WebSocketListener() {

                    override fun onOpen(
                        webSocket: WebSocket,
                        response: Response
                    ) {

                        runOnUiThread {

                            statusText.text =
                                "Connected to MachPulse"
                        }
                    }


                    override fun onMessage(
                        webSocket: WebSocket,
                        text: String
                    ) {

                        runOnUiThread {

                            statusText.text =
                                "Server: $text"
                        }
                    }


                    override fun onClosing(
                        webSocket: WebSocket,
                        code: Int,
                        reason: String
                    ) {

                        runOnUiThread {

                            statusText.text =
                                "Server closing connection"
                        }
                    }


                    override fun onClosed(
                        webSocket: WebSocket,
                        code: Int,
                        reason: String
                    ) {

                        runOnUiThread {

                            if (monitoring) {
                                statusText.text =
                                    "Disconnected"
                            }
                        }
                    }


                    override fun onFailure(
                        webSocket: WebSocket,
                        t: Throwable,
                        response: Response?
                    ) {

                        runOnUiThread {

                            statusText.text =
                                "Connection error"

                            sensorText.text =
                                t.message
                                    ?: "WebSocket failed"
                        }
                    }
                }
            )
    }


    override fun onSensorChanged(
        event: SensorEvent?
    ) {

        if (!monitoring) {
            return
        }


        if (event == null) {
            return
        }


        if (
            event.sensor.type !=
            Sensor.TYPE_ACCELEROMETER
        ) {
            return
        }


        /*
         * Android provides timestamps in
         * nanoseconds for sensor events.
         */
        if (
            firstSensorTimestampNs == 0L
        ) {

            firstSensorTimestampNs =
                event.timestamp
        }


        lastSensorTimestampNs =
            event.timestamp


        xSamples.add(
            event.values[0]
        )

        ySamples.add(
            event.values[1]
        )

        zSamples.add(
            event.values[2]
        )


        updateSampleRate()


        runOnUiThread {

            sampleText.text =
                "Samples: ${xSamples.size} / $WINDOW_SIZE"
        }


        if (
            xSamples.size >=
            WINDOW_SIZE
        ) {

            sendSensorWindow()
        }
    }


    private fun updateSampleRate() {

        val count =
            xSamples.size


        if (
            count < 2 ||
            lastSensorTimestampNs <=
            firstSensorTimestampNs
        ) {
            return
        }


        val elapsedSeconds =
            (
                lastSensorTimestampNs -
                    firstSensorTimestampNs
            ) / 1_000_000_000.0


        if (elapsedSeconds <= 0.0) {
            return
        }


        val sampleRate =
            (count - 1) /
                elapsedSeconds


        runOnUiThread {

            rateText.text =
                "Sample rate: ${
                    "%.1f".format(
                        sampleRate
                    )
                } Hz"
        }
    }


    private fun sendSensorWindow() {

        val socket =
            webSocket

        if (socket == null) {

            clearSamples()

            return
        }


        val sampleRate =
            calculateSampleRate()


        val payload =
            JSONObject()


        payload.put(
            "machine_id",
            MACHINE_ID
        )


        /*
         * Unix timestamp in seconds.
         */
        payload.put(
            "timestamp",
            System.currentTimeMillis()
                / 1000.0
        )


        payload.put(
            "sample_rate",
            sampleRate
        )


        val accelerometer =
            JSONObject()


        accelerometer.put(
            "x",
            JSONArray(xSamples)
        )


        accelerometer.put(
            "y",
            JSONArray(ySamples)
        )


        accelerometer.put(
            "z",
            JSONArray(zSamples)
        )


        payload.put(
            "accelerometer",
            accelerometer
        )


        val sent =
            socket.send(
                payload.toString()
            )


        if (!sent) {

            runOnUiThread {

                statusText.text =
                    "Failed to send sensor data"
            }
        }


        clearSamples()
    }


    private fun calculateSampleRate(): Double {

        if (
            xSamples.size < 2 ||
            lastSensorTimestampNs <=
            firstSensorTimestampNs
        ) {

            return 100.0
        }


        val elapsedSeconds =
            (
                lastSensorTimestampNs -
                    firstSensorTimestampNs
            ) / 1_000_000_000.0


        if (elapsedSeconds <= 0.0) {
            return 100.0
        }


        return (
            xSamples.size - 1
        ) / elapsedSeconds
    }


    private fun clearSamples() {

        xSamples.clear()
        ySamples.clear()
        zSamples.clear()


        firstSensorTimestampNs =
            0L

        lastSensorTimestampNs =
            0L


        runOnUiThread {

            sampleText.text =
                "Samples: 0 / $WINDOW_SIZE"
        }
    }


    override fun onAccuracyChanged(
        sensor: Sensor?,
        accuracy: Int
    ) {
        // Not required for the MVP.
    }


    override fun onDestroy() {

        monitoring = false


        sensorManager.unregisterListener(
            this
        )


        webSocket?.close(
            1000,
            "Application closed"
        )


        webSocket = null


        httpClient.dispatcher
            .executorService
            .shutdown()

        httpClient.connectionPool
            .evictAll()


        super.onDestroy()
    }
}