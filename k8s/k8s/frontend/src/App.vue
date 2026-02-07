<script setup>
import { ref, onMounted, computed } from 'vue'

// Configuration de la langue chargée depuis l'API
const language = ref('fr')

// Dictionnaire de traductions
const translations = {
  fr: {
    flag: '🇫🇷',
    title: 'Kube-Messenger',
    dataSource: 'Source des données',
    yourName: 'Votre nom',
    message: 'Message...',
    send: 'Envoyer',
    readOnlyMode: 'Mode lecture seule : Base de données principale HS.',
    cannotPost: 'Impossible de poster : la base de données principale est hors ligne.',
    sendError: 'Erreur lors de l\'envoi.',
    backendUnreachable: 'ERREUR - Backend inaccessible'
  },
  en: {
    flag: '🇬🇧',
    title: 'Kube-Messenger',
    dataSource: 'Data source',
    yourName: 'Your name',
    message: 'Message...',
    send: 'Send',
    readOnlyMode: 'Read-only mode: Main database is down.',
    cannotPost: 'Cannot post: main database is offline.',
    sendError: 'Error sending message.',
    backendUnreachable: 'ERROR - Backend unreachable'
  }
}

const t = computed(() => translations[language.value] || translations.fr)

const messages = ref([])
const sourceInfo = ref('')
const newMessage = ref({ author: '', content: '' })
const dbStatus = ref({ pg: false, redis: false, loading: true })
const postError = ref('')

// Charger la configuration
const loadConfig = async () => {
  try {
    const res = await fetch('/api/config')
    const data = await res.json()
    language.value = data.language || 'fr'
  } catch (e) {
    console.error('Failed to load config:', e)
  }
}

// Fonction pour charger les messages
const loadMessages = async () => {
  try {
    // En K8s, on passera par l'Ingress, donc chemin relatif
    const res = await fetch('/api/messages')
    const data = await res.json()
    messages.value = data.data
    sourceInfo.value = data.source
  } catch (e) {
    sourceInfo.value = t.value.backendUnreachable
  }
}

// Check status (Readiness probe du back)
const checkStatus = async () => {
    try {
        const res = await fetch('/api/readyz')
        if(res.ok) {
            const data = await res.json()
            dbStatus.value = { pg: data.pg, redis: data.redis, loading: false }
        } else { throw new Error() }
    } catch (e) {
         dbStatus.value = { pg: false, redis: false, loading: false }
    }
}

// Poster un message
const postMsg = async () => {
  postError.value = ''
  if(!dbStatus.value.pg) {
      postError.value = t.value.cannotPost
      return
  }
  try {
    await fetch('/api/messages', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(newMessage.value)
    })
    newMessage.value.content = '' // Reset form
    loadMessages() // Reload view
  } catch (e) {
      postError.value = t.value.sendError
  }
}

// Boucle de rafraichissement
onMounted(() => {
  loadConfig()
  loadMessages()
  checkStatus()
  setInterval(() => { loadMessages(); checkStatus(); }, 5000)
})
</script>

<template>
  <div class="container">
    <div class="header">
      <h1>{{ t.flag }} {{ t.title }}</h1>
    </div>

    <div class="status-bar">
        {{ t.dataSource }}: <strong>{{ sourceInfo }}</strong> |
        Postgres: <span :class="dbStatus.pg ? 'green' : 'red'">{{ dbStatus.pg ? 'OK' : 'DOWN' }}</span> |
        Redis: <span :class="dbStatus.redis ? 'green' : 'red'">{{ dbStatus.redis ? 'OK' : 'DOWN' }}</span>
    </div>

    <div class="post-form" :class="{ disabled: !dbStatus.pg }">
        <input v-model="newMessage.author" :placeholder="t.yourName" :disabled="!dbStatus.pg">
        <input v-model="newMessage.content" :placeholder="t.message" :disabled="!dbStatus.pg">
        <button @click="postMsg" :disabled="!dbStatus.pg">{{ t.send }}</button>
        <p v-if="postError" class="error">{{ postError }}</p>
        <p v-if="!dbStatus.pg && dbStatus.redis" class="warning">{{ t.readOnlyMode }}</p>
        <p v-if="!dbStatus.pg && !dbStatus.redis" class="error">.</p>

    </div>

    <ul>
      <li v-for="(msg, index) in messages" :key="index">
        <strong>{{ msg.author }}:</strong> {{ msg.content }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
/* CSS Basique pour le TP */
.container { max-width: 800px; margin: 0 auto; font-family: sans-serif; }
.header { text-align: center; margin-bottom: 20px; }
.header h1 { margin: 10px 0; }
.status-bar { background: #f0f0f0; padding: 10px; margin-bottom: 20px; border-radius: 5px;}
.green { color: green; font-weight: bold; }
.red { color: red; font-weight: bold; }
.post-form { background: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
.post-form.disabled { opacity: 0.6; }
.error { color: red; }
.warning { color: orange; font-weight: bold;}
input, button { margin: 5px; padding: 8px; }
ul { list-style-type: none; padding: 0; }
li { background: #f9f9f9; margin: 5px 0; padding: 10px; border-left: 4px solid #007bff; }
</style>