# <----------------------------------------------------------------------------------------->
#  Stage 1: Base Runtime & Lockfile Dependencies
# <----------------------------------------------------------------------------------------->
FROM node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32 AS base

WORKDIR /app

#Enable libc6 compatibility for alphine if any native bindings exists
RUN apk add --no-cache libc6-compat 

# Install dependencies based on yarn.lock
COPY package*.json yarn.lock ./
RUN yarn install --frozen-lockfile --perfer-offline

# <----------------------------------------------------------------------------------------->
#  Stage 2: Devlepment (Hot reload + bind mount target)
# <----------------------------------------------------------------------------------------->
FROM base AS dev

WORKDIR /app

ENV NODE_ENV=devlopment \
	PORT=3000 \
	HOSTNAME="0.0.0.0"

# copy source as fallback (local bind mounts override this in compose)
COPY . .

EXPOSE 3000

CMD ["yarn", "dev"]

# <----------------------------------------------------------------------------------------->
#  Stage 3: Production Builder
# <----------------------------------------------------------------------------------------->
FROM base AS builder

WORKDIR /app
COPY . .

ENV NODE_ENV=production \
	NEXT_TELEMETRY_DISABLED=1

RUN yarn build

# <----------------------------------------------------------------------------------------->
#  Stage 4: Production Runner {Ultra-lean standalone output}
# <----------------------------------------------------------------------------------------->
# copy source as fallback (local bind mounts override this in compose)
FROM node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32 AS prod

WORKDIR /app

ENV NODE_ENV=production \
	NEXT_TELEMETRY_DISABLED=1 \
	PORT=3000 \
	HOSTNAME="0.0.0.0"

RUN addgroup --system --grid 1001 nodejs && \
	adduser --system -uid 1001 nextjs

COPY --from=builder /app/public ./public

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["yarn", "server.js"]