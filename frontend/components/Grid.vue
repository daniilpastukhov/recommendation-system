<template>
  <v-container class="grid">
    <masonry :cols="3" :gutter="30">
      <div v-for="game in games">
        <Card :id="game.id" :title="game.name" :description="game.description" :genres="game.genres"
              :img_url="game.img_url" :like_action="like" :dislike_action="dislike" :show_delete="false"
              :show_like="showLike(game)" :show_dislike="showDislike(game)" show_link="true" />
      </div>
    </masonry>
    <v-row class="justify-center load_button">
      <v-btn @click="getGames()">Get games</v-btn>
    </v-row>
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
            async getGames(limit = 6) {
                let response = await this.$axios.post('/games', {"limit": limit})
                console.log(response.data)
                for (let type of ['random_games', 'liked_games', 'disliked_games']) {
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
            },
            async like(id) {
                await this.$axios.post('/games/like', {"id": id})
            },
            async dislike(id) {
                await this.$axios.post('/games/dislike', {"id": id})
            },
            async delete(id) {
                await this.$axios.post('/games/delete', {"id": id})
            },
            removeGame(id) {
                for (let i = 0; i < this.games.length; i++) {
                    if (this.games[i]['id'] === id) {
                        this.games.splice(i, 1)
                        break
                    }
                }
            },
            showLike(game) {
                return game['type'] !== 'liked_games';
            },
            showDislike(game) {
                return game['type'] !== 'disliked_games';
            }
        },
        created() {
            this.getGames()
        }
    }
</script>

<style scoped>
  .grid {
    margin-top: 48px;
  }

  .load_button {
    margin: 32px 0;
  }
</style>
