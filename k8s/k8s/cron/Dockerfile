FROM alpine:3.18

# Installation du client PostgreSQL
RUN apk add --no-cache postgresql-client bash

WORKDIR /scripts
COPY cleanup.sh .
RUN chmod +x cleanup.sh

# Création d'un user non-root
RUN adduser -D cronuser
USER cronuser

# Au démarrage du container, on lance le script
CMD ["./cleanup.sh"]