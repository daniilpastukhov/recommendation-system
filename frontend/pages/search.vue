<template>
  <v-container class="grid">
    <masonry :cols="3" :gutter="30">
      <div v-for="game in games">
        <Card :id="game.id" :title="game.name" :description="game.description" :genres="game.genres"
              :img_url="game.img_url" :like_action="like" :dislike_action="dislike" :show_like="showLike(game)"
              :show_dislike="showDislike(game)" show_link="true"/>
      </div>
    </masonry>
  </v-container>
</template>

<script>
    import Card from '~/components/Card.vue'

    export default {
        components: {
            Card
        },
        data() {
            return {
                games: []
            }
        },
        props: {},
        methods: {
            async search() {
                this.games = []
                console.log(this.$store.state.search_text)
                let response = await this.$axios.post('/games/search', {'text': this.$store.state.search_text})
                console.log(response.data)
                for (let type of ['all_games', 'liked_games', 'disliked_games']) {
                    console.log(response.data[type])
                    let data = JSON.parse(response.data[type])
                    for (let i = 0; i < data.length; i++) {
                        let game = data[i]
                        this.games.push({
                            "id": game.appid,
                            "name": game.name,
                            "description": game.short_description.replace('&quot;', '').replace('&amp;', '').replace('&nbsp;', ''),
                            "genres": game.genres.split(";").join(", "),
                            "img_url": game.header_image,
                            "type": type
                        })
                    }
                }
                this.$store.commit('SET_SEARCH_TEXT', '')
            },
            async like(id) {
                await this.$axios.post('/games/like', {"id": id})
            },
            async dislike(id) {
                await this.$axios.post('/games/dislike', {"id": id})
            },
            showLike(game) {
                return game['type'] !== 'liked_games';
            },
            showDislike(game) {
                return game['type'] !== 'disliked_games';
            }
        },
        created() {
            this.search()
        },
        watch: {
            '$store.state.search_text': function () {
                if (this.$store.state.search_text.length) this.search()
            }
        },
        middleware: 'auth'
    }
</script>

<style scoped>
  .grid {
    margin-top: 48px;
  }
</style>
