// ===============================
// Biblioteca do Servo
// ===============================
#include <Servo.h>

// ===============================
// Definição dos pinos dos servos
// ===============================
#define pinBase        9
#define pinBraco       10
#define pinAntebraco   11
#define pinGarra       6

// ===============================
// Objetos Servo
// ===============================
Servo Base;
Servo Braco;
Servo Antebraco;
Servo Garra;

// ===============================
// Tamanho da média móvel
// ===============================
#define NUM 15

// ===============================
// Vetores de leitura + posições atuais
// ===============================
int leitura_Base[NUM];
int leitura_Braco[NUM];
int leitura_Antebraco[NUM];
int leitura_Garra[NUM];

int posBase = 90;
int posBraco = 90;
int posAntebraco = 90;
int posGarra = 90;

void setup() {
  Serial.begin(9600);

  Base.attach(pinBase);
  Braco.attach(pinBraco);
  Antebraco.attach(pinAntebraco);
  Garra.attach(pinGarra);

  // Inicializa vetores
  for (int i = 0; i < NUM; i++) {
    leitura_Base[i] = 90;
    leitura_Braco[i] = 90;
    leitura_Antebraco[i] = 90;
    leitura_Garra[i] = 90;
  }

  // Posição inicial
  Base.write(90);
  Braco.write(90);
  Antebraco.write(90);
  Garra.write(90);

  Serial.println("Pronto! Envie comandos:");
  Serial.println("Exemplo: 90,45,120,30");
  Serial.println("Ou: B90  R120  A60  G30");
}

void loop() {
  // Lê comandos da Serial
  if (Serial.available()) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();

    // Formato: 90,45,120,30
    if (comando.indexOf(',') > 0) {
      int valores[4];
      int idx = 0;
      String temp = "";

      for (int i = 0; i < comando.length(); i++) {
        char c = comando.charAt(i);
        if (c == ',' || i == comando.length() - 1) {
          if (i == comando.length() - 1) temp += c;
          valores[idx++] = constrain(temp.toInt(), 0, 180);
          temp = "";
          if (idx >= 4) break;
        } else {
          temp += c;
        }
      }

      if (idx == 4) {
        posBase = valores[0];
        posBraco = valores[1];
        posAntebraco = valores[2];
        posGarra = valores[3];
      }
    }
    // Formato individual: B90, R45, A120, G30
    else if (comando.length() >= 2) {
      char eixo = comando.charAt(0);
      int valor = constrain(comando.substring(1).toInt(), 0, 180);

      switch (eixo) {
        case 'B': case 'b': posBase = valor; break;
        case 'R': case 'r': posBraco = valor; break;   // R de "braço"
        case 'A': case 'a': posAntebraco = valor; break;
        case 'G': case 'g': posGarra = valor; break;
      }
    }
  }

  // Aplica média móvel e move os servos
  media_movel(posBase, posBraco, posAntebraco, posGarra);

  delay(15);
}

// ===============================
// Função de média móvel (suavização)
// ===============================
void media_movel(int pBase, int pBraco, int pAnte, int pGarra) {
  long soma_Base = 0, soma_Braco = 0, soma_Ante = 0, soma_Garra = 0;

  // Desloca os valores
  for (int i = NUM - 1; i > 0; i--) {
    leitura_Base[i] = leitura_Base[i - 1];
    leitura_Braco[i] = leitura_Braco[i - 1];
    leitura_Antebraco[i] = leitura_Antebraco[i - 1];
    leitura_Garra[i] = leitura_Garra[i - 1];
  }

  // Insere novas posições
  leitura_Base[0] = pBase;
  leitura_Braco[0] = pBraco;
  leitura_Antebraco[0] = pAnte;
  leitura_Garra[0] = pGarra;

  // Soma
  for (int i = 0; i < NUM; i++) {
    soma_Base += leitura_Base[i];
    soma_Braco += leitura_Braco[i];
    soma_Ante += leitura_Antebraco[i];
    soma_Garra += leitura_Garra[i];
  }

  // Move os servos
  Base.write(soma_Base / NUM);
  Braco.write(soma_Braco / NUM);
  Antebraco.write(soma_Ante / NUM);
  Garra.write(soma_Garra / NUM);
}