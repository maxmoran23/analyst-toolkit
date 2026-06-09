plugins {
    kotlin("jvm") version "2.0.21"
    kotlin("plugin.serialization") version "2.0.21"
    application
}

group = "org.maxmoran"
version = "0.1.0"

repositories {
    mavenCentral()
}

dependencies {
    // JSON I/O — matches the design principle of the Python quant lib (JSON in, JSON out)
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")

    // Numerical primitives (distributions, matrix decomp) — used sparingly; only where pure Kotlin would
    // duplicate well-tested math (e.g., inverse normal CDF, Cholesky). Most modules are dependency-free.
    implementation("org.apache.commons:commons-math3:3.6.1")

    testImplementation(kotlin("test"))
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.3")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

java {
    toolchain {
        // OpenJDK 21 LTS — pinned for reproducibility. The audit-defensible JVM choice for this repo.
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

kotlin {
    jvmToolchain(21)
}

application {
    // Single CLI entrypoint: ./gradlew run --args="kelly --mode single --p 0.55 --odds 2.0"
    // Cli.kt dispatches to per-module runners (runKelly, runSharpe, ...).
    mainClass.set("org.maxmoran.quant.CliKt")
}

tasks.test {
    useJUnitPlatform()
    testLogging {
        events("passed", "skipped", "failed")
        showStandardStreams = false
    }
}
