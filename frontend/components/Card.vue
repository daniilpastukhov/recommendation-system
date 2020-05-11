<template>
  <v-card class="mx-auto card" max-width="400">
    <v-img class="white--text align-end" height="200px" :src="img_url">
      <v-card-title>{{ title }}</v-card-title>
    </v-img>

    <v-card-subtitle class="pb-0">{{ genres }}</v-card-subtitle>

    <v-card-text class="text--primary">
      <div>{{ description }}</div>
    </v-card-text>

    <v-card-actions class="justify-center action-menu">
      <v-btn v-if="like" class="like_button" color="green" append-icon="thumb_up" text
             @click="like_action(id); switchButton('like')">Like
        <v-icon size="17" right>thumb_up</v-icon>
      </v-btn>
      <v-btn v-if="dislike" class="dislike_button" color="red" append-icon="thumb_down" text
             @click="dislike_action(id); switchButton('dislike')">Dislike
        <v-icon size="17" right>thumb_down</v-icon>
      </v-btn>
      <v-btn v-if="show_delete" class="delete_button" append-icon="delete" text
             @click="delete_action(id)">Delete
        <v-icon size="17" right>delete</v-icon>
      </v-btn>
      <v-btn v-if="show_link" :href="'https://store.steampowered.com/app/' + id" target="_blank">
        <v-icon left>fab fa-steam</v-icon>
        Steam
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
    export default {
        data() {
            return {
                like: this.show_like,
                dislike: this.show_dislike
            }
        },
        props: {
            id: {
                type: Number,
                required: true
            },
            title: {
                type: String,
                required: true
            },
            description: {
                type: String,
                required: true
            },
            genres: {
                type: String,
                required: true
            },
            img_url: {
                String,
                required: true
            },
            like_action: {
                Function,
                required: true
            },
            dislike_action: {
                Function,
                required: true
            },
            show_like: {
                Boolean,
                required: true
            },
            show_dislike: {
                Boolean,
                required: true
            },
            show_delete: {
                Boolean,
                required: false
            },
            delete_action: {
                Function,
                required: false
            },
            show_link: false
        },
        methods: {
            switchButton(type) {
                if (this.like && this.dislike) {
                    if (type === 'like') this.like = false
                    else this.dislike = false
                } else if (this.like && !this.dislike) {
                    this.like = false
                    this.dislike = true
                } else if (!this.like && this.dislike) {
                    this.like = true
                    this.dislike = false
                }
            }
        }
    }
</script>

<style>
  .card {
    margin: 20px auto;
  }

  .action-menu {
    margin-bottom: 10px;
  }
</style>
