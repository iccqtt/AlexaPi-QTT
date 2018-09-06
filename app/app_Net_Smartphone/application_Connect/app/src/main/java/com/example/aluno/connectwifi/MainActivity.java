package com.example.aluno.connectwifi;

import android.content.Context;
import android.os.StrictMode;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import com.example.aluno.connectwifi.R;

import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.Toast;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.PasswordAuthentication;
import java.net.URL;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        final Context mContext = getApplicationContext();
        final AutoCompleteTextView mTextSSID = (AutoCompleteTextView) findViewById(R.id.SSID_TextInput);
        final AutoCompleteTextView mTextPassword = (AutoCompleteTextView) findViewById(R.id.Password_TextInput);
        final Button button_send = (Button) findViewById(R.id.ButtonHttp);
        button_send.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View v) {
                button_send.setBackgroundColor(getResources().getColor(R.color.LightDark));
                String SSID = mTextSSID.getText().toString();
                String Password = mTextPassword.getText().toString();
                if(!(SSID.equals("") || Password.equals("")) || Password.length() < 8){
                    InternetConnection T = new InternetConnection(SSID, Password);
                    Thread thread = new Thread(T);
                    thread.start();
                }
                else{
                    Toast.makeText(mContext.getApplicationContext(),"Cannot Enter, please check your entry",
                            Toast.LENGTH_SHORT).show();
                }
                button_send.setBackgroundColor(getResources().getColor(R.color.Dark));
            }
        });

    }
}
