#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define LED_VERDE 25
#define LED_AMARELO 26
#define LED_VERMELHO 27
#define BUZZER 14
#define BUTTON 4

LiquidCrystal_I2C lcd(0x27, 16, 2);

struct AlertaMunicipio {
  const char* municipio;
  const char* estado;
  const char* bioma;
  const char* risco;
};

AlertaMunicipio alertas[] = {
  {"Apui", "AM", "Amazonia", "medio"},
  {"Labrea", "AM", "Amazonia", "baixo"},
  {"Novo Progresso", "PA", "Amazonia", "alto"},
  {"Altamira", "PA", "Amazonia", "medio"},
  {"Porto Velho", "RO", "Amazonia", "alto"},
  {"Corumba", "MS", "Pantanal", "medio"},
  {"Porto Murtinho", "MS", "Pantanal", "baixo"},
  {"Pocone", "MT", "Pantanal", "medio"},
  {"Barao Melgaco", "MT", "Pantanal", "medio"}
};

int indiceAtual = 0;
int totalAlertas = 9;

int ultimoEstadoBotao = HIGH;

void desligarAlertas() {
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(LED_AMARELO, LOW);
  digitalWrite(LED_VERMELHO, LOW);
  digitalWrite(BUZZER, LOW);
}

void exibirLCD(String linha1, String linha2) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(linha1.substring(0, 16));
  lcd.setCursor(0, 1);
  lcd.print(linha2.substring(0, 16));
}

void emitirPulsoBuzzer(int quantidade, int tempoMs) {
  for (int i = 0; i < quantidade; i++) {
    digitalWrite(BUZZER, HIGH);
    delay(tempoMs);
    digitalWrite(BUZZER, LOW);
    delay(tempoMs);
  }
}

void alertaBaixo(String municipio, String estado) {
  desligarAlertas();
  digitalWrite(LED_VERDE, HIGH);

  exibirLCD(
    municipio + "-" + estado,
    "Risco: BAIXO"
  );
}

void alertaMedio(String municipio, String estado) {
  desligarAlertas();
  digitalWrite(LED_AMARELO, HIGH);

  exibirLCD(
    municipio + "-" + estado,
    "Risco: MEDIO"
  );
}

void alertaAlto(String municipio, String estado) {
  desligarAlertas();
  digitalWrite(LED_VERMELHO, HIGH);

  exibirLCD(
    municipio + "-" + estado,
    "Risco: ALTO"
  );

  emitirPulsoBuzzer(3, 250);
}

void registrarOcorrenciaLocal() {
  desligarAlertas();

  digitalWrite(LED_VERMELHO, HIGH);

  exibirLCD(
    "OCORRENCIA",
    "CONFIRMADA"
  );

  Serial.println("------");
  Serial.println("OCORRENCIA LOCAL CONFIRMADA");
  Serial.println("Validacao humana registrada pela estacao ESP32.");
  Serial.println("Acionamento manual realizado em campo.");
  Serial.println("Fonte: operador local / human-in-the-loop");

  emitirPulsoBuzzer(5, 180);

  delay(3000);

  digitalWrite(LED_VERMELHO, LOW);

  exibirLCD(
    "Registro salvo",
    "Monitorando..."
  );

  delay(1500);
}

void processarRisco(AlertaMunicipio alerta) {
  String risco = alerta.risco;
  risco.toLowerCase();

  String municipio = alerta.municipio;
  String estado = alerta.estado;

  if (risco == "baixo") {
    alertaBaixo(municipio, estado);
  } else if (risco == "medio") {
    alertaMedio(municipio, estado);
  } else if (risco == "alto") {
    alertaAlto(municipio, estado);
  } else {
    desligarAlertas();

    exibirLCD(
      municipio + "-" + estado,
      "Risco invalido"
    );
  }

  Serial.println("------");
  Serial.println("Sentinela Orbital IA - Estacao ESP32");

  Serial.print("Municipio: ");
  Serial.print(alerta.municipio);
  Serial.print(" - ");
  Serial.println(alerta.estado);

  Serial.print("Bioma: ");
  Serial.println(alerta.bioma);

  Serial.print("Risco recebido: ");
  Serial.println(alerta.risco);

  Serial.println("Fonte: Dashboard Web / Orquestrador Multiagente");
  Serial.println("Funcao da estacao: alerta local e validacao humana em campo");
}

bool botaoPressionado() {
  int estadoAtual = digitalRead(BUTTON);

  if (ultimoEstadoBotao == HIGH && estadoAtual == LOW) {
    ultimoEstadoBotao = estadoAtual;
    delay(50);
    return true;
  }

  ultimoEstadoBotao = estadoAtual;
  return false;
}

void setup() {
  Serial.begin(115200);

  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_AMARELO, OUTPUT);
  pinMode(LED_VERMELHO, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);

  lcd.init();
  lcd.backlight();

  desligarAlertas();

  exibirLCD(
    "Sentinela IA",
    "Estacao local"
  );

  delay(2000);

  exibirLCD(
    "Human-in-loop",
    "ativo"
  );

  delay(1500);

  exibirLCD(
    "Inicializando",
    "alertas..."
  );

  delay(1500);
}

void loop() {
  if (botaoPressionado()) {
    registrarOcorrenciaLocal();
  }

  AlertaMunicipio alertaAtual = alertas[indiceAtual];

  processarRisco(alertaAtual);

  unsigned long inicio = millis();

  while (millis() - inicio < 6000) {
    if (botaoPressionado()) {
      registrarOcorrenciaLocal();
      break;
    }

    delay(50);
  }

  indiceAtual++;

  if (indiceAtual >= totalAlertas) {
    indiceAtual = 0;
  }
}