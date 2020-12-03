using UnityEngine;
using System.Collections;
using Nethereum.JsonRpc.UnityClient;
using Nethereum.Hex.HexTypes;
using Nethereum.Contracts;
using Nethereum.RPC.Eth.DTOs;
using System.Numerics;
using Nethereum.ABI;
using Nethereum.Signer;
using Nethereum.Hex.HexConvertors.Extensions;
using System;
using Newtonsoft.Json;

public class Account : MonoBehaviour
{
    // Here we define accountAddress (the public key; We are going to extract it later using the private key)
    private string accountAddress;
    // This is the secret key of the address, you should put yours.
    private string accountPrivateKey = "poistettu";
    // This is the testnet we are going to use for our contract, in this case kovan
    private string _url = "poistettu";
    // contract address
    private static string contractAddress = "poistettu";
    // We define a new contract (Netherum.Contracts)
    private Contract contract;

    // Use this for initialization
    void Start()
    {
        // First we'll call this function which will extract and assign the public key from the accountPrivateKey defined above.
        importAccountFromPrivateKey();  
        Debug.Log("Account import OK");

        // hae priva account hash
        StartCoroutine(getAccount());

        //// check balance of imported account
        //StartCoroutine(getAccountBalance(accountAddress, (balance) => {
        //    Debug.Log("Account balance: " + balance);
        //}));
    }


    private string account_hash;
    private IEnumerator getAccount()
    {
        var req = new EthAccountsUnityRequest(_url);
        yield return req.SendRequest();
        if (req.Exception == null)
        {
            Debug.Log("Account 0: " + req.Result[0]);
            account_hash = req.Result[0];
            // get wallet
            Debug.Log("Getting wallet...");
            StartCoroutine(getWallet());
        }
        else
        {
            throw new InvalidOperationException("Get account request failed");
        }
    }

    private bool walletFound = false;
    private string wallet_hash;
    private IEnumerator getWallet()
    {
        string[] molemmat = parseJSON("WalletDB.json");

        // new request
        var req = new EthSendTransactionUnityRequest(_url);

        // new contract from contract address
        var contract = new Contract(null, molemmat[0], account_hash);
        Function func = contract.GetFunction("getWallet");
        TransactionInput ti = func.CreateTransactionInput(account_hash);

        yield return req.SendRequest(ti);
        if (req.Exception == null)
        {
            Debug.Log("Wallet found: " + req.Result);
            wallet_hash = req.Result;
            walletFound = true;
            // get assets from wallet
            Debug.Log("Getting assets...");
            StartCoroutine(getAssets());
        }
        else
        {
            throw new InvalidOperationException("Get wallet request failed");
        }
    }

    private string asset_hash;
    public IEnumerator getAssets()
    {
        // read json and get abi and bytecode
        string[] molemmat = parseJSON("GameWallet.json");
        // new request
        var req = new EthSendTransactionUnityRequest(_url);
        // new contract and wanted function from contract address
        var contract = new Contract(null, molemmat[0], account_hash);
        var func = contract.GetFunction("getAssets");
        TransactionInput ti = func.CreateTransactionInput(account_hash);

        yield return req.SendRequest(ti);
        if (req.Exception == null)
        {
            asset_hash = req.Result;
            // assetin tiedot
            StartCoroutine(getAssetInfo());
        }
        else
        {
            throw new InvalidOperationException("Get assets request failed");
        }
    }


    private IEnumerator getAssetInfo()
    {
        string[] molemmat = parseJSON("Asset.json");
        // new request
        var req = new EthSendTransactionUnityRequest(_url);

        // new contract from contract address
        var contract = new Contract(null, molemmat[0], account_hash);
        Function func = contract.GetFunction("getRock");
        TransactionInput ti = func.CreateTransactionInput(account_hash);
        yield return req.SendRequest(ti);
        if (req.Exception == null)
        {
            Debug.Log("Info found: " + req.Result);
        }
        else
        {
            throw new InvalidOperationException("Get info request failed");
        }
    }
    // turhat  alkaa tästä

    public IEnumerator getAccountBalance(string address, System.Action<decimal> callback)
    {
        var getBalanceRequest = new EthGetBalanceUnityRequest(_url);
        yield return getBalanceRequest.SendRequest(address, BlockParameter.CreateLatest());
        if (getBalanceRequest.Exception == null)
        {
            var balance = getBalanceRequest.Result.Value;
            callback(Nethereum.Util.UnitConversion.Convert.FromWei(balance, 18));
        }
        else
        {
            throw new InvalidOperationException("Get balance request failed");
        }

    }

    public void importAccountFromPrivateKey()
    {
        // Here we try to get the public address from the secretKey we defined
        try
        {
            var address = EthECKey.GetPublicAddress(accountPrivateKey);
            // Then we define the accountAdress private variable with the public key
            accountAddress = address;
        }
        catch (Exception e)
        {
            // If we catch some error when getting the public address, we just display the exception in the console
            Debug.Log("Error importing account from PrivateKey: " + e);
        }
    }

    private string[] parseJSON(string jsonfile)
    {
        string jsonString = System.IO.File.ReadAllText("Assets/JSON/" + jsonfile);
        var parsed = Newtonsoft.Json.Linq.JObject.Parse(jsonString);
        string ABIstring = parsed.GetValue("abi").ToString();
        string BCstring = parsed.GetValue("bytecode").ToString();
        var molemmat = new string[] { ABIstring, BCstring };
        return molemmat;
    }
}