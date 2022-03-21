# DexGuru-ETHDenver

You can use this bot to track prices and volume of tokens , to set price and volume alerts and also to get specific wallet information and transactions. All in one!

Get live coin price and volume- Get live price and volume of any token across chains. All you have to do it put a message in the below format
- /price,chainName,tokenTicker

- /volume,chainName,tokenTicker

Supported Chains - ethereum,bsc,polygon,avalanche,arbitrum,fantom,celo,optimism

Price Alerts: You can also set price and volume alerts for any token. Put in a message in the below format:
Set Price Alert:-

**/price,operation,chainName,tokenTicker,priceInUSD**

Set Volume Alert:-

**/volume,operation,chainName,tokenTicker,priceInUSD**

where operation - "higher" or "lower"

/alerts to check alerts

/clear to clear all alerts

3)Wallet info and transactions:

Get wallet info and recent 5 transaction swap details along with etherscan link using the following commands:-

/walletinfo,chainName,walletAddress - Gives generic info about the wallet

/wallettransactions,chainName,walletAddress - Displays the token swapped in , out and the amount along with the etherscan/bscscan link of the transaction hash of the 5 latest swaps of the given wallet.



Sample Commands:- 

1) Price and Volume 

/price,bsc,bnb

/volume,bsc,bnb

2) Price and Volume Alerts

/price,higher,bsc,cake,10

/volume,lower,bsc,cake,60000

3) Wallet Details

/walletinfo,bsc,0x818F478aCC50b8eC70799Cf89767112A61b33e6c

/wallettransactions,bsc,0x818F478aCC50b8eC70799Cf89767112A61b33e6c
