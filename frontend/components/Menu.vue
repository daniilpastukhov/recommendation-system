<template>
  <v-app-bar app color="primary" dense fixed>
    <v-btn text to="/" color="white">Game recommendation system</v-btn>
    <v-btn text to="/rate" color="white">Rate games</v-btn>
    <v-btn text to="/recommendation" color="white">Recommendation</v-btn>
    <v-spacer/>
    <v-text-field
      v-model="search_text"
      @keyup.enter="updateData()"
      placeholder="Ex. Counter Strike"
      append-icon="search"
      dark
      dense
      clearable
      style="margin-bottom: -11px; max-width: 250px"
    ></v-text-field>
    <div v-if="$auth.loggedIn">
      <v-btn text to="/profile" color="white">{{ $auth.user }}</v-btn>
      <v-btn text @click="$auth.logout()" color="white">Logout</v-btn>
    </div>
    <div v-else>
      <v-btn text to="/login" color="white">Login</v-btn>
      <v-btn text to="/register" color="white">Register</v-btn>
    </div>
  </v-app-bar>
</template>

<script>
    export default {
        data() {
            return {
                search_text: ''
            }
        },
        methods: {
            updateData() {
                console.log('data updated')
                this.$store.commit('SET_SEARCH_STATUS', true)
                this.$store.commit('SET_SEARCH_TEXT', this.search_text)
                this.$router.push('/search')
                // this.$router.go({'path': '/search'})
            }
        }
    }
</script>

<style scoped>
</style>
