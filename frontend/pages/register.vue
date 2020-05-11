<template>
    <div class="auth">
        <!-- <h1>Login</h1> -->
        <AuthForm buttonText="Register" :submitForm="registerUser" class="authForm" :hasName="true"
            title="Registration form" />
    </div>
</template>

<script>
import AuthForm from '~/components/AuthForm.vue'

export default {
  components: {
    AuthForm
  },
  methods: {
    async registerUser(registrationInfo) {
        let response = await this.$axios.post('/register', registrationInfo)
        console.log(response)
        await this.$auth.loginWith('local', {
            data: registrationInfo
          })
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