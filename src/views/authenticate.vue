<template>
  <div class="flex flex-col items-center justify-center">
    <div class="flex items-center gap-5">
      <svg
        class="animate-spin h-5 w-5 text-gray-500"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        ></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>

      <div>
        <h1 class="font-medium">Authenticating</h1>
        <p class="text-sm">Verifying authentication, this wont be long...</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { useRoute, useRouter } from "vue-router";
import { BACKEND_SIGNUP_AUTH } from "@/constants";
import { onMounted } from "vue";
import { useApi } from "@/services/api";

const route = useRoute();
const router = useRouter();
const code = route.query.code as string;

onMounted(async () => {
  if (!code) {
    const url = new URL(BACKEND_SIGNUP_AUTH);
    url.searchParams.set(
      "flash",
      "Error, could'nt derive user, Try signing in"
    );
    return window.open(url, "_self");
  }

  // const { data: user } = await

  useApi("[PO] /auth/exchange", {
    data: {
      code,
    },
    args: null,
    params: null,
  })
    .then(async ({ data: authtoken }) => {
      localStorage.setItem("authtoken", authtoken.token);

      const { data: store } = await useApi(
        "[GE] /api/user/last-viewed-store",
        {
          data: null,
          args: null,
          params: null,
        },
        true
      );

      if (store) {
        return router.replace({
          name: "dashboard-home",
          params: {
            id: store.id,
          },
        });
      }

      return router.replace({
        name: "create-store",
      });
    })
    .catch(() => {
      const url = new URL(BACKEND_SIGNUP_AUTH);
      url.searchParams.set("flash", "Error deriving token");
      return window.open(url, "_self");
    });
});
</script>
