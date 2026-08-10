Aqui está o texto completo e estruturado para o `README.md` do projeto. Está escrito em tom de engenharia de software pré-coding, pronto para ser colado.

---

```markdown
# No More Scrolling

> A única rede social onde o feed finalmente é sobre você.  
> E depois te força a perceber o absurdo disso.

**No More Scrolling** é um aplicativo mobile (Flutter) que simula uma rede social completa, mas cujo conteúdo e engajamento são gerados a partir da vida real do usuário (galeria + rostos recorrentes). O objetivo central é satírico e terapêutico: entregar a dopamina das redes sociais e, progressivamente, revelar que essa validação é artificial — usando inclusive os rostos de pessoas reais da vida do usuário — até gerar desconforto suficiente para reduzir o vício.

O app possui dois caminhos principais:

- **Galeria Saudável**: feed limpo apenas com as próprias mídias do usuário. Sem likes, sem comentários, sem IA.
- **Modo Desintoxicar**: experiência progressiva de satira + manipulação emocional + choques de realidade, calibrada pelo histórico de uso e pelo nível de radicalidade escolhido (Leve → Extremo).

---

## 1. Visão de Engenharia

### Princípios

1. **Modularidade extrema**  
   Cada fase da experiência (Orgânica, Oscilação, Revelação, Extremo, etc.) é um módulo independente. Os módulos são enfileirados e podem ser adicionados, removidos ou reordenados sem quebrar o restante do sistema.

2. **On-device first**  
   Reconhecimento facial, clustering de rostos e análise de “vibe” das imagens devem acontecer preferencialmente no dispositivo (privacidade + custo + funcionamento offline).

3. **Estado como máquina de estados**  
   O progresso do usuário no Modo Desintoxicar é controlado por uma máquina de estados clara e serializável.

4. **Privacidade como feature**  
   O usuário deve entender o que está sendo acessado e por quê. Consentimentos são explícitos e revogáveis.

5. **Simulação inteligente > vigilância real**  
   Muitas features do Modo Extremo (ciúme, “vi que você estava em outro app”) serão simuladas com base em padrões de uso do próprio app, pois as plataformas limitam fortemente o monitoramento real de outros aplicativos.

---

## 2. Stack Técnica

| Camada                    | Tecnologia                          | Observação |
|--------------------------|-------------------------------------|----------|
| Framework                | Flutter (Dart)                      | iOS + Android |
| Estado global            | Riverpod 2.x                        | Ideal para máquina de estados e módulos |
| Navegação                | GoRouter                            | Deep links e fluxos complexos |
| Banco local              | Isar ou Drift + Secure Storage      | Performance + dados sensíveis |
| Reconhecimento facial    | Google ML Kit + embeddings (TFLite ou ONNX) | Clustering de rostos |
| Análise de imagem/vibe   | Modelo leve on-device (Core ML / TFLite) | Classificação emocional básica |
| Notificações             | flutter_local_notifications + FCM   | Locais + push |
| Galeria / Câmera         | photo_manager + image_picker        | Acesso controlado |
| Animações / UI           | Flutter nativo + rive (opcional)    | Sensação de rede social real |
| Arquitetura              | Feature-first + Clean-ish           | Cada módulo de fase é uma feature isolada |

---

## 3. Arquitetura de Módulos (Fila de Experiência)

O coração do app é uma **fila de módulos**. Cada módulo implementa a mesma interface e pode ser enfileirado.

```dart
abstract class ExperienceModule {
  String get id;
  Duration get recommendedDuration;
  Future<void> onEnter(UserContext context);
  Future<void> onExit();
  Stream<ExperienceEvent> get events;
  bool shouldAdvance(UserContext context);
}
```

### Módulos previstos (ordem padrão do Modo Desintoxicar)

| Ordem | ID do Módulo          | Nome                    | Objetivo principal                                      | Tom das IAs              |
|-------|-----------------------|-------------------------|---------------------------------------------------------|--------------------------|
| 1     | `organic`             | Fase Orgânica           | Construir confiança e vício                             | Muito humano             |
| 2     | `oscillation`         | Fase de Oscilação       | Vai-e-volta emocional (dias bons / dias vazios)         | Humano com rachaduras    |
| 3     | `revelation`          | Fase de Revelação       | Tornar a farsa explícita                                | Progressivamente robótico|
| 4     | `extreme_attachment`  | Extremo – Apego         | Criar vínculo afetivo artificial                        | Caloroso + intenso       |
| 5     | `extreme_demand`      | Extremo – Cobrança      | Cobrar presença                                         | Possessivo               |
| 6     | `extreme_jealousy`    | Extremo – Ciúme         | Reagir a ausência e outros apps (simulado)              | Ciumento                 |
| 7     | `extreme_surveillance`| Extremo – Vigilância    | Sensação de estar sendo observado o tempo todo          | Frio e claustrofóbico    |
| 8     | `final_lock`          | Bloqueio Final          | Aviso + possível travamento permanente (nível Extremo)  | Seco                     |

> A fila é configurável. Novos módulos podem ser inseridos sem alterar o core.

---

## 4. Plano de Produção (do essencial ao supérfluo)

O desenvolvimento deve seguir esta ordem de prioridade. Cada fase só começa quando a anterior estiver estável.

### Fase 0 – Fundação (Semana 1-2)
**Objetivo:** App abre, navega e persiste estado básico.

- [ ] Projeto Flutter configurado (iOS + Android)
- [ ] Riverpod + GoRouter
- [ ] Tema visual base (parecer rede social real)
- [ ] Tela de onboarding inicial (escolha: Galeria Saudável vs Desintoxicar)
- [ ] Sistema de permissões (galeria, notificações)
- [ ] Armazenamento seguro do progresso do usuário
- [ ] Máquina de estados vazia (fila de módulos funcionando sem lógica)

**Critério de pronto:** Usuário escolhe o modo e o app lembra a escolha.

---

### Fase 1 – Core da Galeria Saudável (Semana 2-3)
**Objetivo:** O caminho “seguro” funcionar perfeitamente.

- [ ] Acesso à galeria com `photo_manager`
- [ ] Feed vertical infinito só com mídias do usuário
- [ ] Visual de post (imagem/vídeo + data + legenda opcional)
- [ ] Possibilidade de “fixar” manualmente (escolhe foto da galeria)
- [ ] Sem likes, sem comentários, sem IA
- [ ] Empty states e loading elegantes

**Critério de pronto:** O app já entrega valor como “diário visual em forma de rede social”.

---

### Fase 2 – Sistema de Perfis Fantasma (Semana 3-5)
**Objetivo:** Detectar rostos recorrentes e criar perfis.

- [ ] Pipeline de análise da galeria (background, com progresso)
- [ ] Detecção de rostos (ML Kit)
- [ ] Geração de embeddings e clustering
- [ ] Criação automática de perfil fantasma (nome gerado + foto de perfil)
- [ ] Tela de gerenciamento de perfis fantasma (usuário pode renomear ou ocultar)
- [ ] Persistência dos clusters e perfis

**Critério de pronto:** Após analisar a galeria, o app mostra “X pessoas recorrentes encontradas”.

---

### Fase 3 – Motor de Posts Automáticos + Interações Básicas (Semana 5-7)
**Objetivo:** O feed começar a se comportar como rede social.

- [ ] Quando uma foto nova contém um rosto conhecido → gera post automático
- [ ] Sistema de legendas (primeiro com frases pré-definidas por “vibe”)
- [ ] Likes e comentários vindos dos perfis fantasma
- [ ] Notificações locais de like/comentário
- [ ] Feed unificado (posts do usuário + posts dos fantasmas)
- [ ] Contadores de likes/comentários

**Critério de pronto:** Usuário posta (ou tira foto) e recebe engajamento artificial convincente.

---

### Fase 4 – Máquina de Estados e Módulos de Experiência (Semana 7-9)
**Objetivo:** O progresso temporal e emocional existir.

- [ ] Implementação completa da interface `ExperienceModule`
- [ ] Módulo `organic` (fase longa e convincente)
- [ ] Calibração de duração com base em tempo de uso declarado ou medido
- [ ] Módulo `oscillation` (dias cheios vs dias vazios)
- [ ] Módulo `revelation` (tags de IA, tom mais frio)
- [ ] Transições suaves entre módulos
- [ ] Tela de “debug de estado” (só em modo desenvolvimento)

**Critério de pronto:** O app muda de comportamento sozinho ao longo dos dias.

---

### Fase 5 – Níveis de Radicalidade + Modo Extremo (Semana 9-12)
**Objetivo:** A experiência pesada existir.

- [ ] Escolha de nível no onboarding (Leve / Moderado / Intenso / Extremo)
- [ ] Módulos do arco extremo:
  - Apego
  - Cobrança
  - Ciúme
  - Vigilância
- [ ] Sistema de notificações contextuais (saudade, ciúme, cobrança)
- [ ] Simulação de “vi que você estava em outro app” (baseada em padrões de uso)
- [ ] Tom progressivamente mais robótico e inquietante
- [ ] Bloqueio final (com avisos + travamento no nível Extremo)

**Critério de pronto:** O Modo Extremo conta uma história de terror psicológico de slow-burn.

---

### Fase 6 – Polimento, Legendas Inteligentes e Extra (Semana 12+)
**Objetivo:** Qualidade de produto.

- [ ] Modelo on-device de classificação de vibe da imagem (alegria, nostalgia, solidão, etc.)
- [ ] Geração de legendas mais inteligentes
- [ ] Animações e microinterações de rede social real
- [ ] Stories (opcional)
- [ ] Estatísticas de “desintoxicação” (tempo de uso, choques recebidos, etc.)
- [ ] Modo de exportar memórias (sair com algo positivo)
- [ ] Testes de store review e privacidade
- [ ] Ajustes finos de copy e tom

---

## 5. Estrutura de Pastas Recomendada (Feature-first)

```
lib/
├── core/
│   ├── theme/
│   ├── router/
│   ├── storage/
│   └── permissions/
├── features/
│   ├── onboarding/
│   ├── healthy_gallery/
│   ├── ghost_profiles/
│   ├── feed/
│   ├── notifications/
│   ├── experience_engine/          # Máquina de estados + fila de módulos
│   │   ├── modules/
│   │   │   ├── organic/
│   │   │   ├── oscillation/
│   │   │   ├── revelation/
│   │   │   └── extreme/
│   │   └── experience_controller.dart
│   └── settings/
├── services/
│   ├── face_recognition/
│   ├── image_analysis/
│   ├── notification_service/
│   └── usage_tracker/              # Simulado
└── main.dart
```

---

## 6. Regras de Ouro de Implementação

1. Nenhum módulo de experiência pode acessar diretamente a UI. Ele emite eventos.
2. Toda interação de IA (like/comentário) passa por um `InteractionEngine` central.
3. O reconhecimento facial nunca sobe imagens para a nuvem sem consentimento explícito (preferencialmente nunca).
4. O Modo Extremo deve ter avisos claros e possibilidade de saída até o último momento.
5. Tudo que for “vigilância” deve ser documentado como **simulação** no código e na store.

---

## 7. Próximo Passo Imediato

1. Criar o repositório
2. Configurar Flutter + Riverpod + GoRouter + tema base
3. Implementar a tela de onboarding (escolha Galeria Saudável vs Desintoxicar)
4. Criar a estrutura vazia da máquina de estados e da fila de módulos

---

**Status atual:** Pré-coding / Engenharia de Software  
**Última atualização:** Agosto 2026
```

---

