package org.nomiteam.heads;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.SkullMeta;
import java.util.*;
public final class NomiHeads extends BasePlugin {
 protected String commandName(){return "nomiheadbuy";}protected double defaultPrice(){return 100;}
 private record Quote(UUID owner,int slot,ItemStack[] contents,ItemStack head){}
 protected void request(Player p,String[] args){
  if(cancel(p,args))return;
  if(args.length==0){
   int slot=p.getInventory().firstEmpty();if(slot<0||slot>=p.getInventory().getStorageContents().length){p.sendMessage("§c背包没有空位，未扣费。");return;}
   ItemStack head=new ItemStack(Material.PLAYER_HEAD);SkullMeta meta=(SkullMeta)head.getItemMeta();
   meta.setPlayerProfile(p.getPlayerProfile());head.setItemMeta(meta);
   Quote quote=new Quote(p.getUniqueId(),slot,copy(p.getInventory().getStorageContents()),head);
   String token=confirmations.issue(p.getUniqueId(),quote,price,System.currentTimeMillis());
   confirmation(p,"购买本人头像费用："+price+"（仅可使用一次）。",token);return;
  }
  if(args.length!=2||!args[0].equalsIgnoreCase("confirm")){p.sendMessage("§c只能购买本人头像；请使用 /nomiheadbuy 生成确认。");return;}
  var preview=confirmations.take(p.getUniqueId(),args[1],System.currentTimeMillis());
  if(preview==null){p.sendMessage("§c确认已过期或已使用，请重新输入 /nomiheadbuy。");return;}
  Quote q=(Quote)preview.state();
  result(p,transactions.run(p.getUniqueId().toString(),preview.token(),preview.fee(),new Transaction.Port(){
   boolean attempted;
   public void prepared(String tx)throws Exception{
    Properties proof=new Properties();proof.setProperty("owner",q.owner().toString());proof.setProperty("fee",Double.toString(preview.fee()));proof.setProperty("slot",Integer.toString(q.slot()));proof.setProperty("confirmation",preview.token());proof.setProperty("item","PLAYER_HEAD");
    Evidence.save(getDataFolder().toPath().resolve("evidence"),tx,proof);
   }
   public boolean valid(){return p.isOnline()&&economyReady()&&p.hasPermission(permission())&&q.owner().equals(p.getUniqueId())&&preview.fee()==price&&Arrays.equals(q.contents(),p.getInventory().getStorageContents())&&p.getInventory().getItem(q.slot())==null;}
   public boolean charge(double f){return NomiHeads.this.charge(p,f);}
   public void apply(){attempted=true;p.getInventory().setItem(q.slot(),q.head().clone());if(!q.head().equals(p.getInventory().getItem(q.slot())))throw new IllegalStateException("头像发放验证失败");}
   public boolean rollback(){if(!attempted)return true;ItemStack current=p.getInventory().getItem(q.slot());if(current==null)return true;if(!q.head().equals(current))return false;p.getInventory().setItem(q.slot(),null);return p.getInventory().getItem(q.slot())==null;}
   public boolean refund(double f){return NomiHeads.this.refund(p,f);}
  },false));
 }
 private static ItemStack[] copy(ItemStack[] items){return Arrays.stream(items).map(i->i==null?null:i.clone()).toArray(ItemStack[]::new);}
}
