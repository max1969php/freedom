import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}

// Chiave di release opzionale: keystore.properties (storeFile, storePassword, keyAlias, keyPassword).
// Senza, la release è firmata con la chiave debug: si installa lo stesso, ma non va su Play Store.
val keystoreProps = Properties().apply {
    val f = rootProject.file("keystore.properties")
    if (f.exists()) f.inputStream().use { load(it) }
}

android {
    namespace = "com.freedom.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.freedom.app"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }

    signingConfigs {
        if (keystoreProps.isNotEmpty()) {
            create("release") {
                storeFile = rootProject.file(keystoreProps.getProperty("storeFile"))
                storePassword = keystoreProps.getProperty("storePassword")
                keyAlias = keystoreProps.getProperty("keyAlias")
                keyPassword = keystoreProps.getProperty("keyPassword")
            }
        }
    }

    // Python, yt-dlp e FFmpeg sono librerie native da ~30 MB per CPU: un APK per CPU più uno universale.
    // L'universale è quello da distribuire: alcuni telefoni a 64 bit hanno Android a 32 bit.
    splits {
        abi {
            isEnable = true
            reset()
            include("arm64-v8a", "armeabi-v7a")
            isUniversalApk = true
        }
    }

    // youtubedl-android legge Python dai .so estratti su disco.
    packaging {
        jniLibs { useLegacyPackaging = true }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.findByName("release") ?: signingConfigs.getByName("debug")
            // yt-dlp e le sue dipendenze lavorano per riflessione: R8 le rompe (esperienza di ASD).
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true }
    testOptions { unitTests.isReturnDefaultValues = true }
}

// x86 serve solo agli emulatori del PC: fuori dalla release, così l'APK universale ha solo ARM.
androidComponents {
    onVariants(selector().withBuildType("release")) { variant ->
        variant.packaging.jniLibs.excludes.addAll(listOf("lib/x86/**", "lib/x86_64/**"))
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.material.icons.extended)
    debugImplementation(libs.androidx.compose.ui.tooling)

    // La libreria dichiara appcompat ma non lo usa: ~1 MB di risorse risparmiate.
    implementation(libs.youtubedl.android) { exclude(group = "androidx.appcompat") }
    implementation(libs.youtubedl.ffmpeg) { exclude(group = "androidx.appcompat") }

    testImplementation(libs.junit)
}
