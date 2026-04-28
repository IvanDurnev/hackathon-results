<template>
  <div class="app-shell">
    <Toast />
    <ConfirmDialog />
    <router-view />
  </div>
</template>

<script>
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';

export default {
  name: 'App',
  components: { Toast, ConfirmDialog },
};
</script>
