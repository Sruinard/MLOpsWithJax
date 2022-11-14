import { ApolloServer } from "apollo-server";
import { ApolloGateway } from "@apollo/gateway";

const gateway = new ApolloGateway({
  serviceList: [
    {
      name: "alphabrain",
      url: process.env.ALPHABRAIN_ENDPOINT
      // url: 'https://microbraingraphql--2jjxl8i.jollypebble-cb4fc58a.westeurope.azurecontainerapps.io/graphql'
    },
  ],
  experimental_pollInterval: 2000,
});

const server = new ApolloServer({
  gateway,
  subscriptions: false,
});

server
  .listen({ port: 7000 })
  .then(({ url }) => {
    console.info(`🚀 Gateway available at ${url}`);
  })
  .catch((err) => console.error("❌ Unable to start gateway", err));
