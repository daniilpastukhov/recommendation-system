<template>
  <div class="auth">
    <AuthForm buttonText="Login" :submitForm="loginUser" class="authForm" title="Login form"/>
  </div>
</template>

<script>
    import AuthForm from '~/components/AuthForm.vue'

    export default {
        components: {
            AuthForm
        },
        methods: {
            async loginUser(loginInfo) {
                try {
                    await this.$auth.loginWith('local', {
                        data: loginInfo
                    })

                    this.$store.commit('SET_LOGIN_STATUS', '')
                } catch (err) {
                    this.$store.commit('SET_LOGIN_STATUS', 'Something went wrong...')
                    console.log(err)
                }
            }
        }
    }

</script>

<style>
  /* .auth {
    display: flex;
    flex-direction: column;
    text-align: center;
    align-items: center;
    justify-content: center;
    height: 60vh;
    width: 100%;
} */

</style>
