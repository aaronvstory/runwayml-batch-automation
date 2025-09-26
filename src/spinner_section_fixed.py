        # Clear screen completely and start fresh
        console.clear()
        console.print(header_panel)
        
        try:
            if not self.verbose_logging:
                # Configuration panel
                config_table = Table.grid(padding=0)
                config_table.add_column(style="cyan", justify="left", width=15)
                config_table.add_column(style="white", justify="left")
                
                config_table.add_row("Files Amt:", f"{total_files} GenX files")
                config_table.add_row("Driver video:", Path(self.config['driver_video']).name)
                config_table.add_row("Output folder:", "Downloads")
                config_table.add_row("Verbose mode:", "Hidden")
                
                config_panel = Panel(
                    config_table,
                    title="Configuration",
                    border_style="green",
                    title_align="left"
                )
                console.print(config_panel)
                
                # BOTH Rich Progress bar + colorful spinners working together
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    MofNCompleteColumn(), 
                    TextColumn("•"),
                    TimeElapsedColumn(),  # This provides real-time elapsed time
                    console=console
                ) as progress:
                    
                    main_task = progress.add_task("📊 [cyan]0% complete[/cyan] • 🎬 Processing GenX files... 🚀", total=total_files)
                    
                    # Colorful spinner status system
                    status_text = "Loading..."
                    processed = 0
                    
                    def create_colorful_spinners():
                        # Activity spinner - bright green
                        activity_text = Text()
                        activity_text.append("Activity: ", style="bright_green bold")
                        activity_text.append(status_text, style="bright_cyan")
                        activity_spinner = Spinner("dots", text=activity_text, style="bright_green")
                        
                        # Action spinner - bright blue  
                        action_text = Text()
                        action_text.append("Action: ", style="bright_blue bold")
                        action_text.append("Monitoring for interrupts...", style="bright_white")
                        action_spinner = Spinner("dots", text=action_text, style="bright_blue")
                        
                        # Next spinner - bright magenta
                        next_text = Text()
                        next_text.append("Next: ", style="bright_magenta bold")
                        remaining = [Path(f).name for f in folders if generator.get_genx_image_files(f)]
                        if remaining and processed < total_files:
                            display = remaining[:3]
                            folder_list = ", ".join(display)
                            if len(remaining) > 3:
                                folder_list += f" (+{len(remaining)-3} more)"
                            next_text.append(folder_list, style="bright_yellow")
                        else:
                            next_text.append("All processing complete", style="bright_green")
                        next_spinner = Spinner("dots", text=next_text, style="bright_magenta")
                        
                        return Group(activity_spinner, action_spinner, next_spinner)
                    
                    # Display 3 colorful spinners below progress bar
                    with Live(create_colorful_spinners(), console=console, refresh_per_second=10) as live:
                        def update_spinners(new_status):
                            nonlocal status_text
                            status_text = new_status
                            live.update(create_colorful_spinners())
                        
                        # Process files with BOTH progress bar AND spinner updates
                        for folder in folders:
                            folder_name = Path(folder).name
                            genx_images = generator.get_genx_image_files(folder)
                            
                            if not genx_images:
                                continue
                            
                            specific_output = Path(self.config['output_folder'])
                            
                            for image_path in genx_images:
                                image_name = Path(image_path).name
                                
                                # Update BOTH displays
                                status_text = f"Generating: {image_name}"
                                progress.update(main_task, description=f"🎬 [cyan]Generating:[/cyan] {image_name}")
                                update_spinners(status_text)
                                
                                try:
                                    result = generator.create_act_two_generation(
                                        character_image_path=image_path,
                                        output_folder=str(specific_output)
                                    )
                                except Exception as e:
                                    result = None
                                
                                processed += 1
                                completion_pct = int((processed / total_files) * 100) if total_files > 0 else 0
                                
                                if result:
                                    progress.update(main_task, 
                                        completed=processed,
                                        description=f"📊 [cyan]{completion_pct}% complete[/cyan] • ✅ {image_name}")
                                    update_spinners(f"Completed: {image_name}")
                                else:
                                    progress.update(main_task, 
                                        completed=processed,
                                        description=f"📊 [cyan]{completion_pct}% complete[/cyan] • ❌ {image_name}")
                                    update_spinners(f"Failed: {image_name}")
                                
                                if self.config['delay_between_generations'] > 0:
                                    time.sleep(self.config['delay_between_generations'])
                        
                        # Final update
                        if total_files > 0:
                            progress.update(main_task, completed=total_files, 
                                description="📊 [cyan]100% complete[/cyan] • 🎉 All files processed!")
                            update_spinners("Processing complete!")
                        
                        time.sleep(2)
