package com.example.aluno.connectwifi;

import android.provider.Settings;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

public class InternetConnection implements Runnable{
    public static String SSID_Send = null;
    public static String Password_Send = null;
    public InternetConnection(String SSID, String Password){
        this.SSID_Send = SSID;
        this.Password_Send = Password;
    }
    public static String executePost(String targetURL) throws JSONException {
        HttpURLConnection connection = null;
        JSONObject cred = new JSONObject();
        String AuthPass = Password_Send;
        String AuthSSID = SSID_Send;
        cred.put("ssid", AuthSSID);
        cred.put("password", AuthPass);
        try {
            //Create connection
            URL url = new URL(targetURL);
            connection = (HttpURLConnection) url.openConnection();
            connection.setDoInput(true);
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestProperty("Accept", "application/json");
            connection.setRequestMethod("POST");
            //connection.setRequestProperty("Content-Length",
            //        Integer.toString(postDataLength));
            //connection.setRequestProperty("Content-Language", "en-US");

            connection.setUseCaches(false);
            connection.setDoOutput(true);
            //Send request
            DataOutputStream wr = new DataOutputStream(connection.getOutputStream());
            wr.writeBytes(cred.toString());
            wr.flush();
            wr.close();

            //Get Response
            InputStream is = connection.getInputStream();
            BufferedReader rd = new BufferedReader(new InputStreamReader(is));
            StringBuilder response = new StringBuilder(); // or StringBuffer if Java version 5+
            String line;
            while ((line = rd.readLine()) != null) {
                response.append(line);
                response.append('\r');
            }
            rd.close();
            return response.toString();
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    @Override
    public void run() {
        try {
            executePost("http://192.168.1.119:3000/ssid");
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }
}
